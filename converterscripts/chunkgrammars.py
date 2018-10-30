# -*- coding: utf-8 -*-
import sys
import re
from lingex import Utteranceoid, IMTSentenceError
import requests
import json
import pprint
import pickle
import codecs
 
class ISOError(ValueError):
    pass
	
glottodic = pickle.load(open('isoglott.pkl', 'rb'))
fileisodic = pickle.load(open('fndic.pkl', 'rb'))

def getIso(fn): 
    f = fn.split('.')[0]
    print f,
    try:
	isos = fileisodic[f]
    except KeyError:  
	print 'iso not found'
	raise ISOError
    if len(isos)>1:
	print 'too many isos found'
	raise ISOError 
    print ''
    return isos[0]


class Language():
    def __init__(self,iso639):
	self.iso639 = iso639 
	self.fromISO()
	
    def fromISO(self):
	try:
	    retval = glottodic[self.iso639]
	except KeyError:
	    address = 'http://glottolog.org/resource/languoid/iso/%s.json' % self.iso639 
	    r = requests.get(address, headers={'content-type': 'application/json'})
	    retval = json.loads(r.text) 
	    glottodic[self.iso639] = retval	
	    pickle.dump(glottodic,open('isoglott.pkl','wb'))
	self.longitude = retval['longitude']
	self.latitude = retval['latitude']
	self.coords = "%s,%s" % (self.longitude,self.latitude)
	self.name = retval['name'] 
	self.glottocode = retval['id']
	self.ancestors = [(x['id'],x['name']) for x in retval['classification']] 
 
	
    
class Chunk:
    def __init__(self, number, title, content, grammar):
	self.title = title
	self.number = number
	self.content = content
	self.grammar = grammar 
	
    def write(self):  
	template = u"""<add><doc>
	<field name="id">{ID}</field>  
	<field name="name">{ID}</field> 
	<field name="language">{lg}</field> 
	{ancestors}
	<field name="iso639-3">{iso}</field> 
	<field name="author">{src}</field>
	<field name="year">{year}</field>
	<field name="location">{coords}</field>  
	<field name="words">{lenws}</field>  
	<field name="chars">{lenchars}</field>  
	<field name="partof">{grammar}</field>  
	<field name="chunknumber">{number}</field>  
	<field name="content">{content}</field>  
	<field name="dtype">chunk</field>  
	</doc></add>	
	""" 
	ancestors = '\n'.join(['<field name="ancestor">%s</field>'%x[1] for x in self.grammar.language.ancestors])
	ID='%s_%s' % (self.grammar.filename,self.number)
	outname = "solr/chk/%s.%s.chk.xml" % (self.grammar.basename,self.number.replace('.','_'))
	out = open(outname,'w') 
	out.write(template.format(ID=ID, 
				    lg = self.grammar.language.name,
				    iso = self.grammar.language.iso639,
				    src = self.grammar.author,
				    coords = "%s,%s" % (self.grammar.language.longitude, self.grammar.language.latitude),
				    lenws = len(self.content.split()),
				    lenchars = len(self.content),
				    content = self.content,
				    number = self.number,
				    ancestors = ancestors,
				    grammar = self.grammar.basename,
				    year = self.grammar.year
				).encode('utf8')
	)
	out.close()
    
class Grammar:
    def __init__(self, filename):
	self.filename = filename
	m = self.P.match(filename)
	self.author = 'Anonymous'
	self.year = -1    
	if m != None:
	    self.author = m.group(1) 
	    self.year = m.group(3) 
	self.basename = filename.split('/')[-1] 
	self.language = Language(getIso(self.basename)) 
	
    chunks = []
    examples = []
    
    P = re.compile('(.*)_(.*)([0-9]{4})')    
    NUMSPLITTER = re.compile('^ *([0-9]+\.[0-9\.]+) *(.{,50})$')
    #                         number portion          title portion, shorter than 50 chars
    
    EXSTART = re.compile('^ *\(([0-9]+)\)')
    EXEND = re.compile(u"""^ *[\u2018\u2019"'`´«»’'′″″«»„””““”“”‹›].+[\u2018\u2019"'`´«»’'′″″«»„””““”“”‹›]*""")
    
    
	
    def fromFile(self,fn): 
	lines = open(fn).readlines()
	content = []
	number = '0'
	title = fn 
	for line in lines:
	    line = line.decode('utf8').replace('\12','')
	    m =  self.NUMSPLITTER.match(line)
	    if m == None:
		content.append(line)
		continue
	    chunk = Chunk(number,title,'\n'.join(content),self)
	    self.chunks.append(chunk)
	    content = []
	    number = m.group(1).strip()
	    title = m.group(2).strip()
	exstartline = 0
	exnr = -1
	for i, line in enumerate(lines):
	    m =  self.EXSTART.match(line)
	    if m != None:
		exnumber = m.group(1)
		exstartline = i
	    m =  self.EXEND.match(line)
	    if m != None:
		exend = i
		if exstartline + 2 == exend:
		    example = [x.decode('utf8') for x in lines[exstartline:exend+1]]
		    self.examples.append(example)
		    
    def writeChunks(self):
	for chunk in self.chunks: 
	    chunk.write()
    
    def writeExamples(self): 
	for i,ex in enumerate(self.examples): 
	    number = ex[0].strip().split()[0]
	    src = ' '.join(ex[0].strip().split()[1:]) #remove initial (123)
	    imt = ex[1]
	    trs = ex[2]
	    u = Utteranceoid(src,translation=trs,src=self.author,language=self.language,filename=self.basename)
	    try:
		u.insertIMT(imt)
	    except IMTSentenceError:  
		continue
	    outname = "solr/ex/%s.%s.ex.xml"% (self.basename,i) 
	    out = open(outname,'w')
	    ID = '%s_ex_%s' % (self.basename,i)
	    out.write(u.solr(ID=ID,number=number).encode('utf8'))
	    out.close()
	    
	
if __name__ == '__main__': 
    fn = sys.argv[1] 
    try:
	g = Grammar(fn)
	g.fromFile(fn)
	g.writeChunks()
	g.writeExamples()   
    except ISOError:
	pass
	