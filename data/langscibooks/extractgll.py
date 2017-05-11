import sys
import re
import pprint
import json
import os

GLL = re.compile('\\gll[ \t]*(.*?) *?\\\\\\\\\n[ \t]*(.*?) *?\\\\\\\\\n[ \t]*\\\\glt[ \t]*(.*?)\n')
TEXTEXT = re.compile('\\\\text(.*?)\{(.*?)\}')
STARTINGQUOTE = "`‘"
ENDINGQUOTE = "'’"

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
    self.srcwordshtml = [self.tex2html(w) for w in self.srcwordstex]
    self.imtwordshtml = [self.tex2html(w) for w in self.imtwordstex]
    
  def tex2html(self,s):
      result = re.sub(TEXTEXT,'<span class="\\1">\\2</span>',s)
      return result
  
  def json(self):
    print(json.dumps(self.__dict__, sort_keys=True, indent=4))
    
  def __str__(self):
    return "%s\n%s\n%s\n" % (self.srcwordshtml,self.imtwordshtml,self.trs)
  
class example()  :
  def __init__(self,s):
    pass
  
  


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

