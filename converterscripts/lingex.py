import re
import pprint
from  occultono import OCCULTONODICT, OCCULTONODICTREV, OCCULTSHORTHANDDIC

class IMTError(ValueError):
    pass

class IMTWordError(IMTError):
    pass

class IMTSentenceError(IMTError):
    pass

OUTERHTML_ =  u"""<head>  
  <title></title>
  <style type="text/css">
 
.item { 
    display: inline;
    float: left;
    margin-right: 2px;
    min-height:40px;
    border: 1px solid black;
} 

.label{
    background: white;
  }
  </style>
</head><body>%s</body></html>"""

OUTERXML_ =  u"""<?xml version="1.0" encoding="UTF-8"?>
%s"""

IMTSPLITTERS = re.compile('[-=~]')
 
	
class Item():
    """ A sentence, word or morpheme with translation, comment and subelements"""
    
    children = None
    parent = None
    label = ''
    translation = ''
    comment = ''
    author =  None
    language = None
    iso639 = None
    
    
    def __init__(self,children,language):
	self.children = children
	self.offspringjoiner = " "
	
    def __str__(self):
	return self.offspringjoiner.join([str(x) for x in self.children])
	
    def flatstring(self):
	return self.offspringjoiner.join([x.flatstring() for x in self.children])
		
    def getLeaves(self,nested = False):
	if nested:
	    return [(ch.getLeaves(nested = True)) for ch in children]
	return [ch.getLeaves() for ch in children]
	
    def newick(self): 
	return "(%s)%s"%(','.join([ch.newick() for ch in self.children]), self.label)
	
    def xml(self, outer= True): 
        childxml = '\n'.join([c.xml(outer=False) for c in self.children]) 
	innerxml = u"""<item>
 <label>{}</label>
  <children>
   {}
  </children>
  </item>""".format(self.label, childxml) 
	if not outer:
	    return innerxml
	return OUTERXML_%innerxml
	
    def html(self, outer=True, level=0): 
        childhtml = '\n'.join([c.html(outer=False, level=level+1) for c in self.children]) 
	innerhtml = u"""<div class="item xlevel{}"> 
 <div class="label">{}</div>
  <div class="children">
   {}
  </div>  
 <div class="translation">{}</div>
  </div>""".format(level,self.label, childhtml, self.translation) 
	if not outer:
	    return innerhtml
	return OUTERHTML_%innerhtml	
	
    def tupl(self): 
	if self.children != []:
	    return [self.label,self.translation,[c.tupl() for c in self.children]]
	return [self.label,self.translation,[]]
        #return "|".join([self.label, self.translation])
        
    def bb(self):
	return self.html(outer=False).replace('<','[').replace('>',']')  
	    

	
	
class Textoid(Item):
    """an item of roughly text length"""
    offspringjoiner = "\n"
	
class Paragraphoid(Item):
    """an item of roughly text length"""
    def __init__(self,s,children=False):
	self.label = s
	self.s = s
	if children:
	    self.children = children
	else:
	    self.children = [Utteranceoid(x) for x in s.split(" | ")]
	
    offspringjoiner = ". "
	
class Utteranceoid(Item):
    """an item of roughly utterance length"""
    def __init__(self,s,children=False, translation=' ', src=None, language=None, filename=''):
	self.label = s
	self.s = s
	if children:
	    self.children = children
	else:
	    self.children = [Wordoid(x) for x in self.s.split()]
	self.translation = translation
	self.src = src
	self.year = -1  
	self.author = 'Anonymous'
	m = self.P.match(filename)  
	if m != None:
	    self.author = m.group(1) 
	    self.year = m.group(3)  
	self.language = language
	
    P = re.compile('(.*)_(.*)([0-9]{4})')    
    
    offspringjoiner = " "
    
    def insertIMT(self,imt):
	tokens = imt.split()
	if len(tokens) != len(self.children):
	    #print self.s
	    #print tokens
	    #print len(tokens), len(self.children)
	    #for x in self.children:
		#print repr(x.s)
	    #print len(tokens),len(self.children)
	    raise IMTSentenceError
	for child, token in zip(self.children, tokens):
	    try:
		child.insertIMT(token)
	    except IMTWordError:
		pass
	    
    def getAdditions(self,trs):
	trs = trs.lower()
	complexity = False
	negations = ('no', 'none', 'not', 'never', 'nowhere', 'nothing', "don't", "does't", "did't", "won't", "would't", "hasn't", "haven't", "hadn't", "neither" , "nor")
	locations = ('at','where', 'between', 'above', 'below', 'front', 'top', 'bottom', 'side', 'nowhere')
	cmtinstrs = ('with',)
	temproles = ('when','always','never', 'then')
	srcroles = ('from',)
	pathroles = ('along',)
	past_references = ('ago','yesterday')
	present_references = ('now','today')
	future_references = ('tomorrow','will', "won't", 'future')
	poss_preds = ('has a ', 'have a ', 'has an ', 'have an ')
	poss_attrs = (' my ', ' your ', ' his ', ' our ', ' their ', "'s")
	sap1 = ('I', 'me', 'my','myself', 'we', 'us', 'our', 'ours', 'ourselves') #no mine bcs of gold mine
	sap2 = ('you', 'your', 'yours', 'yourself', 'yourselves')
	ors = ('or',)
	ands = ('and',)
	nors = ('neither',)
	tnexs = ('until', 'before', 'after', 'during', 'already', 'still', 'yet') 
	cnexs = ('because',)
	fnexs = ('in order to',)
	dqs = ('two','three','four','five','six','seven','eight','nine','ten','eleven', 'twelve', 'dozen', 'twenty', 'hundred', 'thousand', 'million')
	idqs = ('some', 'many', 'several', 'every', 'all')
	uqs = ('every', 'all', 'always')
	nqs = ('nowhere', 'never', 'no one', 'none')
	uqs_combined = ('every',)
	comparatives = ('better', 'more')
	superlatives = ('most','best')
	sufficientives = ('enough',)
	abundantives = ('too much',)
	evids = ('apparently',)
	proximals =  ('here', 'this', 'these')
	distals =  ('those',) # no that or there bcs of polysemy
	presentationals = ('there are', 'there is', 'there was', 'there were')
	conditions = ('if', 'unless')
	embeddings = ('whether',)
	manners = ('how',)
	reflexives = ('myself','yourself','himself','herself','ourselves','yourselves','themselves')
	reciprocals = ('each other',)
	inceptives = ('begin', 'began', 'begun', 'begins', 'beginning', 'start', 'started', 'starting', 'starts')
	terminatives = ('ends', 'ended', 'stops', 'stop', 'stopped')
	repetitives = ('again', )
	modals = ('want','wants','need','needs','must','can','might','may','could', 'should')
	additions = [] 
	
	
	if trs.strip().endswith('?'):
	    additions.append(('speech_acts','question'))
	if trs.strip().endswith('!'): # or txt.strip().endswith('!'):
	    additions.append(('speech_acts','command'))
	#if txt[1].lower() != txt[1]:
	    #print txt
	    #additions.append(('noun','proper_noun'))	
	# multi word expressions
	for poss in poss_preds:
	    if poss in trs:
		additions.append(('posssession','predicative'))
		break
	for a in abundantives:
	    if a in trs:
		additions.append(('grade','abundant'))
		break	    
	for p in presentationals: 
	    if p in trs:
		additions.append(('focus','thetic'))
		break	    
	#for fnex in fnexs:
	    #if fnex in trs: 
		#additions.append(('nexus','final'))
		#complexity = "complex"
		#break
	for r in reciprocals: 
	    if r in trs:
		additions.append(('orientation','reciprocal')) 
	for uq in uqs_combined:
	    if uq in trs:
		additions.append(('quantification','totality'))
	for nq in nqs:
	    if nq in trs:
		additions.append(('quantification','zero'))
		break
	# one word expressions
	for t in trs.split():
	    t = t.replace(',','').replace('.', '').replace('?','').replace('!','')
	    for neg in negations:
		if neg == t:
		    additions.append(('negation','negative'))
		    break
	    for sap in sap1:
		if sap == t:
		    additions.append(('participant','speaker'))
		    break
	    for sap in sap2:
		if sap == t:
		    additions.append(('participant','addressee'))
		    break
	    for poss in poss_attrs:
		if poss == t:
		    additions.append(('posssession','attributive'))
		    break
	    for loc in locations:
		if loc == t: 
		    additions.append(('participant_roles','location'))	
	    for pr in past_references :
		if pr == t: 
		    additions.append(('time','past'))
	    for pr in present_references :
		if pr == t: 
		    additions.append(('time','present'))
	    for fr in future_references :
		if fr == t:  
		    additions.append(('time','future'))
	    for o in ors :
		if o == t:  
		    additions.append(('coordination','disjunctive'))
	    for a in ands :
		if a == t:  
		    additions.append(('coordination','conjunctive'))
	    for tnex in tnexs :
		if tnex == t:  
		    additions.append(('coordination','temporal'))
		    complexity = "complex"
	    #for cnex in cnexs :
		#if cnex == t:  
		    #additions.append(('nexus','causal'))	
		    #complexity = "complex"
	    for x in nors :
		if x == t:  
		    additions.append(('coordination','NOR'))	
	    for cmtinstr in cmtinstrs: 
		if cmtinstr == t:
		    additions.append(('participant_roles','instrumental'))
		    additions.append(('participant_roles','comitative'))
	    for tr in temproles: 
		if tr == t:
		    additions.append(('participant_roles','time')) 
	    for src in srcroles: 
		if src == t:
		    additions.append(('participant_roles','source')) 
	    for p in pathroles: 
		if p == t:
		    additions.append(('participant_roles','path')) 
	    for dq in dqs: 
		if dq == t:
		    additions.append(('quantity','definite'))
	    for idq in idqs: 
		if idq == t:
		    additions.append(('quantity','indefinite'))
	    for uq in uqs: 
		if uq == t:
		    additions.append(('quantity','totality'))
	    for c in comparatives: 
		if c == t:
		    additions.append(('comparison','comparison'))
	    for s in superlatives: 
		if s == t:
		    additions.append(('comparison','superlative'))
	    for s in sufficientives: 
		if s == t:
		    additions.append(('grade','sufficient'))
	    for e in evids: 
		if e == t:
		    additions.append(('evidentiality','other'))
	    for p in proximals: 
		if p == t:
		    additions.append(('distance','proximal'))
	    for d in distals: 
		if d == t:
		    additions.append(('distance','distal'))
	    for c in conditions: 
		if c == t:
		    additions.append(('participant_roles','condition')) 
		    complexity = 'complex'
	    for m in manners: 
		if m == t:
		    additions.append(('participant_roles','manner')) 
	    #for r in reflexives:  
		#if r == t: 
		    #additions.append(('orientation','reflexive'))  
	    for i in inceptives:  
		if i == t: 
		    additions.append(('phase','beginning'))  
	    for te in terminatives:  
		if te == t: 
		    additions.append(('phase','end'))  
	    #for r in repetitives:  
		#if r == t: 
		    #additions.append(('quantification2','iterative'))  
	    for m in modals:  
		if m == t: 
		    additions.append(('modality','modality'))  
	    for e in embeddings: 
		if e == t: 
		    complexity = 'complex'
		    
	if complexity:
	    additions.append(('sentence_type','complex')) 
	return additions
	
    def getIMTString(self):
	glosses = [g for w in self.children for m in w.children for g in IMTSPLITTERS.split(m.translation) ] 
	return u'\n'.join([u'<field name="gloss">%s</field>'%g.strip() for g in set(glosses) ] )   
	
    def removePunctuation(self,w):  
	ps = u'()[]{},.:;!?"'
	for p in ps:
	    w = w.replace(p,u'')
	return w
	
    def getVernacularwords(self):
	return u'\n'.join(
	[u'<field name="vernacularword">%s</field>'%w
	for w 
	in set(self.removePunctuation(self.s).lower().split())])  
	
	
    def getTranslationwords(self):
	return u'\n'.join(
	    [u'<field name="translatedword">%s</field>'%w
	    for w 
	    in  set(self.removePunctuation(self.translation).lower().split())
	    ]
	)  
	
	
    def solr(self,ID='-1',number=0):
	template = u"""<add><doc>
	<field name="id">{ID}</field>   
	<field name="exnumber">{number}</field>   
	<field name="name">{txt}</field> 
	<field name="language">{lg}</field> 
	<field name="iso639-3">{iso}</field> 
	<field name="vernacularsentence">{txt}</field>  
	<field name="translatedsentence">{trs}</field>
	<field name="author">{author}</field>
	<field name="year">{year}</field>
	{ancestors}
	<field name="src">{src}</field>
	<!-- Join --> 
	{vernacularwords} 
	{translationwords} 
	{additions} 
	{occults} 
	{glosses}
	<field name="lingex">{lingex}</field>  
	<field name="location">{coords}</field>  
	<field name="words">{lenws}</field>  
	<field name="chars">{lenchars}</field>  
	<field name="dtype">example</field>  
	</doc></add>"""	 	
	additions = self.getAdditions(self.translation) 
	additionsstring =  u'\n'.join([u'<field name="%s">%s</field>' % a for a in additions ] )   
	occults = [OCCULTONODICTREV[OCCULTSHORTHANDDIC[x]] for x in OCCULTSHORTHANDDIC if x in [y[1] for y in additions]] 
	occults2 = {}
	for o in occults:
	    os = o.split('_')
	    for i,dummy in enumerate(os):
		occults2['_'.join(os[:i+1])] = True
	occultstring = '\n'.join('<field name="occult">%s</field>'%o for o in occults2) 
	#ID = '%s.%s.%s' % (iso,j,i)
	ancestors = '\n'.join(['<field name="ancestor">%s</field>'%x[1] for x in self.language.ancestors])
	
	name = u"%s-%s" % (self.src.encode('utf8'),ID) 
	outstring = template.format(ID=ID, 
			    number=number,
			    txt=self.s,
			    trs=self.translation,
			    author=self.author, 
			    year=self.year, 
			    src =self.src,
			    ancestors =ancestors,
			    vernacularwords=self.getVernacularwords(), 
			    translationwords=self.getTranslationwords(),
			    additions=additionsstring, 
			    occults=occultstring, 
			    lg=self.language.name.replace(' ','_'),
			    iso=self.language.iso639,
			    coords=self.language.coords, 
			    lenws = len(self.s.split()), 
			    lenchars= len(self.s), 
			    glosses=self.getIMTString(),
			    lingex=self.bb())    
	return outstring
			    

	
        
class Wordoid(Item):
    """an item of roughly word length"""
    offspringjoiner = ""
    
    def __init__(self,s,children=False, translation=' '):
	self.label = s
	self.s = s
	if children:
	    self.children = children
	else:
	    self.children = [Morphemoid(x) for x in re.split("([=-])",self.s)][::2]
	self.joiners = [x for x in re.split("([=-])",self.s)][:1][::2]
	self.translation = translation
	
    def __str__(self): 
	return self.s 
	
    def flatstring(self): 
	return self.offspringjoiner.join([x.label for x in self.children])
	
    def getLeaves(self,nested = False):
	if nested:
	    return((s))
	return self.s
	
    def insertIMT(self,word):
	morphemes = IMTSPLITTERS.split(word)
	if len(morphemes) != len(self.children):	    
	    raise IMTWordError     
	for child, token in zip(self.children, morphemes):
	    child.translation = token
	
	
    
class Morphemoid(Item):
    """an item of roughly morpheme length"""
    def __init__(self,s,translation=' '):
	self.label = s
	self.children = [] 
	self.translation = translation 
    def __str__(self): 
	return self.label
	
	
    def newick(self): 
	#return self.translation, self.label
	return  self.label
	
	
	  
    
    
class Morpheme:
    """ a morpheme"""
    
class Affix(Morpheme):
    """ an affix"""
    
class Clitic(Morpheme):
    """ a clitic"""
    
class PreX(Morpheme):
    """a left-attaching thing"""
    
class Prefix(PreX,Affix):
    """a left-attaching thing"""
    rightjoiner = "-"
    
class Preclitic(PreX,Clitic):
    """a left-attaching thing"""
    rightjoiner = "="
    
class PostX(Morpheme):
    """a left-attaching thing """
    leftjoiner = "-"
    
class Postfix(PostX,Affix):
    """a left-attaching thing """
    leftjoiner = "-"
    
class Postclitic(PostX,Clitic):
    """a left-attaching thing """
    leftjoiner = "-"

if __name__ == '__main__':
    t = "In meine-r Bade-wanne bin ich Kapitaen | das ist wunder-schoen"

    p = Paragraphoid(t)
    pprint.pprint(p.newick())

