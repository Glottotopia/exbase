import re
import pickle
import pprint

d = {}
fnstring = re.compile('fn = \{(.*)\}')
lgcodestring = re.compile('lgcode = \{(.*)\}')
fnp = re.compile('[/\\\\](.*?)\.(pdf|zip)')
isop = re.compile('\[(...)\]')

filenames = None

for l in open('fnlgcodes').readlines():
    fnm = fnstring.search(l)
    if fnm != None:
	fng =   fnm.group(1)
	filenames = [x[0] for x in fnp.findall(fng)]
	print filenames
    lgcdm = lgcodestring.search(l)
    if lgcdm != None:
	lgcdg =   lgcdm.group(1)
	isos = isop.findall(lgcdg)
	for fn in filenames:
	    print fn
	    for iso in isos:
		try:
		    d[fn].append(iso)
		except KeyError:
		    d[fn] = [iso]
pickle.dump(d,open('fndic.pkl','wb'))
pprint.pprint(d)

		
