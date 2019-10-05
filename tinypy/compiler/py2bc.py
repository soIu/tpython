from tinypy.compiler.boot import *
import tinypy.compiler.tokenize as tokenize
import tinypy.compiler.parse as parse
import tinypy.compiler.encode as encode

import sys


## called from python
def compile(s, fname):
	if not "tinypy" in sys.version:
		if not '-co' in sys.argv:
			s = preprocess_source(s)
	tokens = tokenize.tokenize(s)
	t = parse.parse(s,tokens)
	r = encode.encode(fname,s,t)
	return r

def main(src, dest):  ## called from tinypy?
	s = read(src)
	r = compile(s,src)
	save(dest, r)

## hartsantler new hacks

def preprocess_source(src, optimize=True, unsafe=False, inspect=False):
	if not optimize:
		return src
	out = []
	for ln in src.splitlines():
		if ln.strip().startswith("for ") and ' in ' in ln and 'range(' in ln:
			tabs = ln.count('\t')
			start = end = None
			loops = ln.split('range(')[-1].split(')')[0]
			if ',' in loops:
				start, end = loops.split(',')
			if unsafe:
				ln = ('\t'*tabs) + ('loop %s:' %loops)  ## this is fast but not fully working
				out.append(ln)
			else:
				itername = ln.split('for ')[-1].split(' in ')[0]
				if start is not None and end is not None:
					## convert to a while loop, which is much faster in tinypy
					out.append(('\t'*tabs) + itername + ('= %s -1' %start) )
					ln = ('\t'*tabs) + 'while %s < %s:' %(itername, end)
					out.append(ln)
					out.append(('\t'* (tabs+1) ) + itername + '+= 1')
				else:
					## convert to a while loop, which is much faster in tinypy
					out.append(('\t'*tabs) + itername + '= -1')
					ln = ('\t'*tabs) + 'while %s < %s:' %(itername, loops)
					out.append(ln)
					out.append(('\t'* (tabs+1) ) + itername + '+= 1')

		else:
			out.append(ln)

	if '--inspect-opt' in sys.argv:
		inspect = True

	if inspect:
		print(src)
		print('-'*80)

	src = '\n'.join(out)
	if inspect:
		raise RuntimeError(src)

	return src
