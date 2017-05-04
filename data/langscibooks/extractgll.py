import sys
import re
import pprint

GLL = re.compile('\\gll[ \t]*(.*?) *?\\\\\\\\\n[ \t]*(.*?) *?\\\\\\\\\n[ \t]*\\\\glt[ \t]*(.*?)\n')

class gll():
  def __init__(self,t):
    self.src=t[0]
    self.imt=t[1]
    self.trs=t[2]
    self.srcwords=self.src.split()
    self.imtwords=self.imt.split()
    
  def __str__(self):
    return "%s\n%s\n%s" % (self.src,self.imt,self.trs)
  
class example()  :
  def __init__(self,s):
    pass
  
  


if __name__ == '__main__':
  filename = sys.argv[1]
  s = open(filename).read()
  examples = []
  glls = GLL.findall(s)
  for g in glls:
    try:
      examples.append(gll(g))
    except ValueError:
      pass
  for ex in examples:
    print(ex)
  

