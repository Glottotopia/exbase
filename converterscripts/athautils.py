

import re
from xml.etree  import ElementTree as ET 
import lingex

import pprint

IMTSPLITTERS = re.compile('[-=;:\.]')

class Language:
    def __init__(self,name,iso,coords):
	self.name=name
	self.iso=iso
	self.coords=coords

class EAF:    
    athasolar = None
    
    def __init__(self,utterancefile, language = None):
	self.utterancefile = utterancefile  
	self.IUfile = utterancefile.replace('-utterance','-Intonation_unit')
	self.wordsfile = utterancefile.replace('-utterance','-words')
	self.posfile = utterancefile.replace('-utterance','-pos')
	self.wordtranslationfile = utterancefile.replace('-utterance','-word_translation')
	self.morphemesfile = utterancefile.replace('-utterance','-morphemes')
	self.IMTfile = utterancefile.replace('-utterance','-IMT')
	self.UTfile = utterancefile.replace('-utterance','-utterance_translation')
	self.language = language
	        
    def __init__(self,utterancefile, language = None, orig='eaf'):
	if orig=='eaf':
	    self.utterancefile = utterancefile  
	    self.IUfile = utterancefile.replace('-utterance','-Intonation_unit')
	    self.wordsfile = utterancefile.replace('-utterance','-words')
	    self.posfile = utterancefile.replace('-utterance','-pos')
	    self.wordtranslationfile = utterancefile.replace('-utterance','-word_translation')
	    self.morphemesfile = utterancefile.replace('-utterance','-morphemes')
	    self.IMTfile = utterancefile.replace('-utterance','-IMT')
	    self.UTfile = utterancefile.replace('-utterance','-utterance_translation')
	if orig=='typecraft':
	    self.utterancefile = utterancefile   
	    self.wordsfile = utterancefile.replace('-phrase','-word')
	    self.posfile = utterancefile.replace('-phrase','-pos')
	    self.wordtranslationfile = None
	    self.morphemesfile = utterancefile.replace('-phrase','-morpheme')
	    self.IMTfile = utterancefile.replace('-phrase','-gloss')
	    self.UTfile = utterancefile.replace('-phrase','-translation') 
	self.language = language 
	self.orig = orig
	    
    def parse(self, orig='eaf'):	
	self.ut_tree = GrAFtree(self.UTfile)
	self.u_tree = GrAFtree(self.utterancefile)
	if orig=='eaf':
	    self.iu_tree = GrAFtree(self.IUfile)
	self.w_tree = GrAFtree(self.wordsfile)
	self.pos_tree = GrAFtree(self.posfile)
	if orig=='eaf':
	    self.wt_tree = GrAFtree(self.wordtranslationfile)
	self.m_tree = GrAFtree(self.morphemesfile)
	self.imt_tree = GrAFtree(self.IMTfile)
	self.edgeclosure(orig=orig) 
	
	
    def edgeclosure(self,orig='eaf'):  
	self.u_tree.edgeclosured = {} 
	if orig=='eaf':
	    self.u_tree.edgeclosured['iu'] = {} 
	self.u_tree.edgeclosured['w'] = {}  
	self.u_tree.edgeclosured['m'] = {}  
	self.u_tree.edgeclosured['imt'] = {}  
	#l = [('iu','w'),('w','wt'),('w','m'),('m','imt')]
	if orig=='eaf':
	    utterances = self.iu_tree.edged
	if orig == 'typecraft':
	    utterances = self.w_tree.edged
	
		
	
	def addToClosureDic(u,uppers,h, level):
	    if h == []:
		return
	    lowertree, lowerstring = h[0]
	    h = h[1:] 
	    for upper in uppers:  
		#print level*' ', upper, lowerstring
		if upper in lowertree.edged:
		    lowers = tuple(lowertree.edged[upper])  
		    #print lowers
		    try: 
			for l in lowers:
			    self.u_tree.edgeclosured[lowerstring][u].append(l)
		    except KeyError: 
			self.u_tree.edgeclosured[lowerstring][u] = list(lowers) 
		    addToClosureDic(u, lowers, h, level+1) 
		     
	
	hierarchy = [(self.m_tree,'m'),(self.imt_tree,'imt')]
	if orig == 'eaf':
	    hierarchy = [(self.w_tree,'w'),(self.m_tree,'m'),(self.imt_tree,'imt')]
	for utterance in utterances: 
	    if orig=='eaf':
		addToClosureDic(utterance,tuple(self.iu_tree.edged[utterance]) ,hierarchy,0)  
	    if orig =='typecraft':
		addToClosureDic(utterance,tuple(self.w_tree.edged[utterance]) ,hierarchy,0)  
		
	#pprint.pprint(self.u_tree.edgeclosured['imt'])
	 
				    
				    
    def computeLingex(self,topnode,orig):
	if orig == 'eaf':
	    u = lingex.Utteranceoid(self.getText(topnode),
		children = [lingex.Utteranceoid(self.iu_tree.textd[iunode],
			    children =  [lingex.Wordoid(self.w_tree.textd[wnode],
				children =  [lingex.Morphemoid(self.m_tree.textd[mnode],
						    translation = self.imt_tree.textd.get(self.imt_tree.edged.get(mnode,[''])[0])
						    ) 					     
					    for mnode 
					    in self.m_tree.edged.get(wnode,[])
					    ],
					)
					for wnode 
					in self.w_tree.edged[iunode]
					]
			    ) 
			    for iunode 
			    in self.iu_tree.edged[topnode]
			    ]
		)
	    return u 
	if orig=='typecraft':	   
	    toptext = self.getText(topnode)
	    u = lingex.Utteranceoid(toptext,
		    children = [lingex.Utteranceoid(toptext,
				children =  [lingex.Wordoid(self.w_tree.textd[wnode],
				    children =  [lingex.Morphemoid(self.m_tree.textd[mnode],
							translation = self.m_tree.meaningd[mnode]
							) 					     
						for mnode 
						in self.m_tree.edged.get(wnode,[])
						],
					    )
					    for wnode 
					    in self.w_tree.edged[topnode]
					    ]
				)  
				]
		    )
	    return u 
	    
	
	
    def getDominationDictionary_(self, upper, lower):
	d  = {}
	for x in upper.textd: 
	    for y in lower.edged: 
		if x == y:   
		    edges = lower.edged[x]
		    for edge in edges:
			try:
			    trs = lower.textd[edge]  
			    d[x].append(trs)
			except KeyError: 
			    d[x] = [trs]	 
	return d
	
    def getText(self,node):
	return self.u_tree.textd[node]	
	
    def getTranslation(self,node):
	return self.ut_tree.textd[self.ut_tree.edged[node][0]]
	
    #def getIMTWords(self,node): 
	#result = []
	#if node in self.u_tree.edgeclosured['imt']: 
	    #result = [ self.imt_tree.textd[x]  for x in self.u_tree.edgeclosured['imt'][node]  ]  
		
	#result =  ' '.join(result).replace('- ','-').replace(' -', '-')
	#return result	
	
    def getIMTGlosses(self,node): 
	#print self.u_tree.edgeclosured['imt']
	tmp = {} 
	if node in self.u_tree.edgeclosured['imt']:  
	    tokens = [ self.imt_tree.textd[x]  for x in self.u_tree.edgeclosured['imt'][node]  ]
	    for token in tokens:
		for imt in  IMTSPLITTERS.split(token):
		    if imt.strip() != '':
			tmp[imt.strip()] = True 
	return tmp.keys()
	 	
	
    #def eaf2solr(language=None, offset=0):
    def eaf2solr(self,orig='eaf'):   
	d = self.getDominationDictionary_(self.u_tree,self.ut_tree)
	#print d
	l = [ (self.u_tree.textd[x], d[x][0]) for x in d ] #there is only one translation per utterance, so we can directly access it at [0]
	topnodes = self.ut_tree.edged.keys() 
	for i,topnode in enumerate(topnodes):  
	    athasolar = AthaSOLR(i, 
				    topnode,
				    self )
	    athasolar.formattemplate()
	    athasolar.write() 

class GrAFtree:
    def __init__(self,f):
	print f
	self.textd = {} 
	self.edged = {}
	self.meaningd = {}
	self.edgeclosured = {}
	self.f = f
	try:
	    self.tree = ET.parse(f)
	except IOError:
	    self.tree = None
	    return
	self.root = self.tree.getroot()
	self.anchors = self.root.findall('.//{http://www.xces.org/ns/GrAF/1.0/}a')
	self.edges = self.root.findall('.//{http://www.xces.org/ns/GrAF/1.0/}edge') 
	for a in self.anchors:
	    ref = a.attrib['ref']
	    try:
		text = a.find('.//{http://www.xces.org/ns/GrAF/1.0/}f[@name="annotation_value"]').text 
	    except AttributeError:
		text = ''
	    self.textd[ref] = text 
	    try:
		meaning = a.find('.//{http://www.xces.org/ns/GrAF/1.0/}f[@name="meaning"]').text 
	    except AttributeError:
		meaning = None
	    self.meaningd[ref] = meaning 
	    #print ref, text
	    #try:
		#text = t.find('.//*/*').text
	    #except AttributeError:
		#text = '' 
	for edge in self.edges:
	    from_ = edge.attrib['from']
	    to_ = edge.attrib['to'] 
	    try:
		self.edged[from_].append(to_ )
	    except KeyError:
		self.edged[from_] = [to_]
		
	self.dominatednodesd = {}

	    
class AthaSOLR:
    def __init__(self,ID,topnode,eaf):
	self.topnode=topnode
	self.language = eaf.language 
	self.src=eaf.utterancefile 
	self.ID="%s-%s-%s"% (self.language.iso,hash(self.src)%1000,ID) 
	#
	self.txt=eaf.getText(topnode)
	self.lenchars = len(self.txt)
	self.vernacularwords = self.txt.split() 
	self.lenwords = len(self.vernacularwords)
	#
	self.translation=eaf.getTranslation(topnode)
	self.translatedwords=set([self.removePunctuation(x) for x in self.translation.split()])
	#
	#self.imtwords=eaf.getIMTWords(topnode)
	self.imtglosses=eaf.getIMTGlosses(topnode)
	self.mn()
	try: 
	    self.lingex = eaf.computeLingex(topnode,eaf.orig) 
	except KeyError:
	    self.lingex = lingex.Item([])
	
    def removePunctuation(self,w):
	ps = '()[]{},.:;!?"'
	for p in ps:
	    w = w.replace(p,'')
	return w

    def mn(self):
	self.vernacularwords = u'\n'.join([u'<field name="vernacularword">%s</field>'%self.removePunctuation(w.strip())  for w in self.vernacularwords ] )  
	self.translationwords = u'\n'.join([u'<field name="translatedword">%s</field>'%self.removePunctuation(w.strip())  for w in self.translatedwords ] ) 
	
    def getIMTString(self,imts):
	return u'\n'.join([u'<field name="gloss">%s</field>'%w.strip() for w in self.imtglosses ] )  
	
    def write(self):
	out = open('solr/%s.xml'%self.ID,'w')
	out.write(self.outstring.encode('utf8'))
	out.close()
	
	
    translation = ''
    docs = []
    

    def formattemplate(self):  
	test = getAdditions(self.translation) 
	#test = []
	additions =  u'\n'.join([u'<field name="%s">%s</field>' % a for a in test ] )   
	#ID = '%s.%s.%s' % (iso,j,i)
	name = u"%s-%s" % (self.src.encode('utf8'),self.ID) 
	self.outstring = template.format(ID=self.ID, 
			    txt=self.txt,
			    trs=self.translation,
			    src=self.src, 
			    vernacularwords=self.vernacularwords, 
			    translationwords=self.translationwords, 
			    additions=additions, 
			    lg=self.language.name.replace(' ','_'),
			    iso=self.language.iso,
			    coords=self.language.coords, 
			    lenws = self.lenwords, 
			    lenchars=self.lenchars, 
			    #imtwords=self.imtwords, 
			    glosses=self.getIMTString(self.imtglosses),
			    lingex=self.lingex.bb())   
			    
			    
template = u"""<add><doc>
<field name="id">{ID}</field>  
<field name="name">{txt}</field> 
<field name="language">{lg}</field> 
<field name="iso639-3">{iso}</field> 
<field name="vernacularsentence">{txt}</field>  
<field name="translatedsentence">{trs}</field>
<field name="author">{src}</field>
<!-- Join --> 
{vernacularwords} 
{translationwords} 
{additions} 
{glosses}
<field name="lingex">{lingex}</field>  
<field name="location">{coords}</field>  
<field name="words">{lenws}</field>  
<field name="chars">{lenchars}</field>  
</doc></add>"""


	
    