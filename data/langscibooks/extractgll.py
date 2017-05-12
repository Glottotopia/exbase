import sys
import re
import pprint
import json
import os

GLL = re.compile('\\gll[ \t]*(.*?) *?\\\\\\\\\n[ \t]*(.*?) *?\\\\\\\\\n+[ \t]*\\\\glt[ \t\n]*(.*?)\n')
TEXTEXT = re.compile('\\\\text(.*?)\{(.*?)\}') 
STARTINGQUOTE = "`‘"
ENDINGQUOTE = "'’"
TEXREPLACEMENTS = [
  (r'\_','_'),
  (r'\textquotedbl','"'),
  (r'\textprimstress','ˈ'),
  (r'\textbackslash',r'\\'),
  (r'\textbar','|'),
  (r'\textasciitilde','~'),
  (r'\textless','<'),
  (r'\textgreater','>'),
  (r'\textrightarrow','→'),
  (r'\textalpha','α'),
  (r'\textbeta','β'),
  (r'\textgamma','γ'),
  (r'\textdelta','δ'),
  (r'\textepsilon','ε'),
  (r'\textphi','φ'),
  (r'\textupsilon','υ'),
  (r'\newline',' '),
  (r'{\ꞌ}','ꞌ'),
  (r'{\ob}','['),
  (r'{\cb}',']'),
  (r'{\db}',' '),
  (r'\nobreakdash','')
]

class gll():
  def __init__(self,src,imt,trs,filename=None,language=None):
    self.filename=filename
    self.src=src
    self.imt=imt
    self.language=language
    self.trs=trs.strip()
    if self.trs[0] in STARTINGQUOTE:
      self.trs = self.trs[1:]
    if self.trs[-1] in ENDINGQUOTE:
      self.trs = self.trs[:-1]
    self.srcwordstex=self.src.split()
    self.imtwordstex=self.imt.split()
    assert(len(self.srcwordstex)==len(self.imtwordstex))
    self.categories = self.tex2categories(imt)
    self.srcwordshtml = [self.tex2html(w) for w in self.srcwordstex]
    self.imtwordshtml = [self.tex2html(w) for w in self.imtwordstex]
    self.srcwordsbare = [self.striptex(w) for w in self.srcwordstex]
    self.imtwordsbare = [self.striptex(w,sc2upper=True) for w in self.imtwordstex]
    self.clength = len(self.src)
    self.wlength = len(self.srcwordsbare)
    self.ID = '%s-%s'%(self.filename.replace('.tex','').split('/')[-1],str(hash('asdfarew ewe'))[:6])
    self.analyze()
    
  def tex2html(self,s):
      result = re.sub(TEXTEXT,'<span class="\\1">\\2</span>',s)
      for r in TEXREPLACEMENTS:        
        result = result.replace(*r)      
      return result
      
  def striptex(self,s,sc2upper=False):
      if sc2upper: 
        for c in self.categories:
          s = re.sub('\\\\textsc{%s}'%c,c.upper(),s)
      result = re.sub(TEXTEXT,'\\2',s)

      for r in TEXREPLACEMENTS:        
        result = result.replace(*r)
      return result
    
  def tex2categories(self,s):
      d = {}
      scs =  re.findall('\\\\textsc\{(.*?)\}',s)
      for sc in scs:
        cats = re.split('[-=.:]',sc)
        for cat in cats: 
          d[cat] = True
      return sorted(list(d.keys()))
    
    
  def json(self):
    print(json.dumps(self.__dict__, sort_keys=True, indent=4))
    
  def __str__(self):
    return "%s\n%s\n%s\n" % (self.srcwordshtml,self.imtwordshtml,self.trs)
  
  def analyze(self):
    if ' and ' in self.trs:
      self.coordination = 'and'
    if ' or ' in self.trs:
      self.coordination = 'or'
    if ' yesterday ' in self.trs.lower():
      self.time = 'past'
    if ' tomorrow ' in self.trs.lower():
      self.time = 'future'
    if ' now ' in self.trs.lower():
      self.time = 'present'
    if ' want' in self.trs.lower():
      self.modality = 'volitive'
    if ' not ' in self.trs.lower():
      self.polarity= 'negative'
  
  
  


if __name__ == '__main__':
  filename = sys.argv[1]
  language = sys.argv[2]
  s = open(filename).read() 
  examples = []
  glls = GLL.findall(s)
  for g in glls:
    try:
      examples.append(gll(*g,filename=filename,language=language))
    except AssertionError:
      pass
    except IndexError:
      pass
  if examples != []:
    jsons = json.dumps([ex.__dict__ for ex in examples], sort_keys=True, indent=4)  
    out = open('jsondata/%sexamples.json'%filename[:-4].replace('/','-'),'w')  
    out.write(jsons)
    out.close()

