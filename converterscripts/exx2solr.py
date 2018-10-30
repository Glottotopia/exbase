# -*- encoding: UTF-8 -*-

import sys
import re
import glob 
import lingex 
from athautils import getAdditions

IMTSPLITTERS = re.compile('[-=~]')
 	
def removePunctuation(w):
    ps = '()[]{},.:;!?"'
    for p in ps:
	w = w.replace(p,'')
    return w
    
def getIMTGlosses(tokens):   
    d={}
    for token in tokens:
	for imt in  IMTSPLITTERS.split(token):
	    if imt.strip() != '':
		d[imt.strip()] = True 
    return d.keys()

	
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
{glosses}
{additions}
<field name="lingex">{lingex}</field>   
<field name="words">{lenws}</field>  
<field name="chars">{lenchars}</field>  
</doc></add>"""

for d in glob.glob('hh/*'): 
    for f in glob.glob('%s/*ex'%d):
	print d, f 
	ex5 = []
	try: 
	    ex1 = open(f).read().decode('utf8').split('\n--\n') 
	    ex2 = [x.split('\n') for x in ex1] 
	    ex3 = [x for x in ex2 if len(x)==3] 
	    ex4 = [x for x in ex3 if len(x[0].split())-1==len(x[1].split())]  
	    ex5 = [x for x in ex4 
		if len(x[2].strip())>0 
		and  x[2].strip()[0]  in u"""\u2018\u2019"'`´«»’'′″″«»„””““”“”‹›""" ] 
	except TypeError:
	    print 'Type error' 
	if ex5 == []:
	    continue
	#print "found %i examples"%len(ex5)
	for i, x in enumerate(ex5):
	    ID = '%s--%s'% (hash(f),i)
	    out = open('%s/solr/%s.xml'%(d,ID), 'w')
	     
	    txt = ' '.join(x[0].split()[1:]) 
	    lenchars = len(txt)
	    lenws = len(txt.split())
	    imt = x[1] 
	    trs = x[2] 
	    iso = d.split()[-1]
	    vernacularwords = u'\n'.join([u'<field name="vernacularword">%s</field>'%removePunctuation(w.strip())  for w in txt.split() ] )  
	    translationwords = u'\n'.join([u'<field name="translatedword">%s</field>'%removePunctuation(w.strip())  for w in trs.split() ] ) 
	    glosses = u'\n'.join([u'<field name="gloss">%s</field>'%w.strip() for w in getIMTGlosses(imt.split()) ] )  
	    additions =  u'\n'.join([u'<field name="%s">%s</field>' % a for a in getAdditions(trs)  ] )  
	    u = lingex.Utteranceoid(txt, translation=trs)
	    u.insertIMT(imt) 
	    lingexx = u.bb()
	    out.write(template.format(ID=ID,
					txt=txt,
					trs=trs,
					lg=iso,
					iso=iso,
					src=f,	
					vernacularwords=vernacularwords,	
					translationwords=translationwords,
					glosses = glosses,lingex=lingexx,lenws=lenws,lenchars=lenchars,additions=additions).encode('utf8'))
	    out.close()
	


	