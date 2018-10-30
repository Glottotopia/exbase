import sys

template = u"""<add><doc>
<field name="id">{ID}</field>  
<field name="name">{txt}</field> 
<field name="language">{iso}</field> 
<field name="iso639-3">{iso}</field> 
<field name="vernacularsentence">{txt}</field>  
<field name="translatedsentence">{trs}</field>
<field name="author">John Doe</field> 
<field name="dtype">example</field> 
{vernacularwords} 
{translationwords}    
</doc></add>"""

iso = sys.argv[1]
f = sys.argv[2]
try:
    print iso,f
    ex1 = open(f).read().decode('utf8').split('\n--\n')
    print len(ex1),
    ex2 = [x.split('\n') for x in ex1]
    print len(ex2),
    ex3 = [x for x in ex2 if len(x)==3]
    print len(ex3),
    ex4 = [x for x in ex3 if len(x[0].split())-1==len(x[1].split())] 
    print len(ex3),
    #ex5 = [x for x in ex4 if u'\u2018' in x[2] and u'\u2019' in x[2]]
    #print len(ex5)
    ex5 = ex4
except:
    pass


for i, x in enumerate(ex5):
    ID = '%s%s'% (hash(f),i)
    out = open('%s.xml'%ID, 'w')
    txt = x[0]
    trs = x[2]
    vernacularwords = u'\n'.join([u'<field name="vernacularword">%s</field>'%w.strip()  for w in txt.split() ] ) 
    translationwords = u'\n'.join([u'<field name="translatedword">%s</field>'%w.strip()  for w in trs.split() ] )
    
    out.write(template.format(ID=ID,txt=txt,trs=trs,lg=iso,iso=iso,vernacularwords=vernacularwords,translationwords=translationwords).encode('utf8'))


