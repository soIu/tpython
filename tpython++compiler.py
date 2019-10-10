#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys, subprocess

def pythonicpp( source ):
	out = []
	prev = None
	prevs = None
	previ = None
	autobrace = 0
	autofunc = 0
	mods = {}
	modname = None
	for ln in source:
		indent = 0
		for c in ln:
			if c == '\t':
				indent += 1

		if indent < previ and autobrace:
			braces = previ - indent
			b = '\t' * indent
			b += '}'*braces
			out.append(b)

		s = ln.strip()

		if s.startswith('@'):
			assert s.startswith('@module')
			assert s.count('(')==1
			assert s.count(')')==1
			modname = s.split('(')[-1].split(')')[0]
			if modname not in mods:
				mods[modname] = []
			out.append('// module: ' + modname)
		elif s.startswith('def '):
			assert s.endswith(':')
			autobrace += 1
			autofunc += 1
			func_name = s[len('def ') : ].split('(')[0]
			if '->' in s:
				returns = s[:-1].split('->')[-1]
			elif prevs.startswith('@module'):
				returns = 'tp_obj'
			else:
				returns = 'void'

			args = []
			rawargs = s.split('(')[-1].split(')')[0]
			for i, arg in enumerate(rawargs.split(',')):
				if arg == 'TP':
					if i != 0:
						raise SyntaxError('ERROR: `TP` must be the first argument')
				elif arg and ' ' not in arg:
					arg = 'auto ' + arg

				if arg:
					args.append( arg )

			if prevs.startswith('@module'):
				if not len(args):
					args.append('TP')
				elif args[0] != 'TP':
					args.insert(0, 'TP')

			#func = '\t' * indent
			func = '%s %s(%s) {' %(returns, func_name, ','.join(args))
			out.append(func)

		elif s.startswith('while ') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			w += 'while(' + s[len('while '):-1] + ') {'
			out.append(w)

		elif s.startswith('if ') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			w += 'if(' + s[len('if '):-1] + ') {'
			out.append(w)

		elif s == 'else:':
			autobrace += 1
			w = '\t' * indent
			w += 'else {'
			out.append(w)
		else:
			if not s.endswith( ('{', '}') ):
				if not s.endswith(';'):
					ln += ';'
			out.append(ln)

		prev = ln
		prevs = s
		previ = indent

	if autofunc:
		out.append('}')

	cpp = '\n'.join(out)
	if '--inspect-pythonic++' in sys.argv:
		raise RuntimeError(cpp)
	return cpp

def metapy2tinypypp( source ):
	shared = []
	right_side = []
	thread_local = []
	thread = None
	cpy = None
	cpp = []
	in_cpp = False
	for ln in source.splitlines():
		if u'┃' in ln:
			assert ln.count(u'┃')==1
			a,b = ln.split(u'┃')
			shared.append(a)
			right_side.append(b)
		elif ln.startswith('with c++:'):
			cpp = []
			in_cpp = True
		elif ln.startswith('with python:'):
			cpy = []
		elif ln.startswith('with thread:'):
			thread = []
			thread_local.append(thread)
		elif in_cpp:
			if not ln.strip():
				in_cpp = False
			else:
				cpp.append(ln)
		elif thread is not None:
			if ln.startswith('\t'):
				thread.append( ln[1:] )
			else:
				thread = None
		elif cpy is not None:
			if ln.startswith('\t'):
				cpy.append( ln[1:] )
			else:
				s = '\n'.join(cpy)
				shared.append("python.run('''%s''')" %s)
				cpy = None
		elif len(right_side) and not ln.strip():
			shared.extend( right_side )
			right_side = []
		else:
			shared.append(ln)

	scripts = []
	if len(thread_local):
		for thread_code in thread_local:
			script = '\n'.join(shared)
			script += '\n'
			script += '\n'.join(thread_code)
			scripts.append(script)
	else:
		script = '\n'.join(shared)
		scripts.append(script)

	cpp = pythonicpp( cpp )
	return scripts, cpp

def main():
	input_file = None
	exargs = []
	for arg in sys.argv[1:]:
		if arg.endswith('.py'):
			input_file = arg
		elif arg.startswith('--'):
			exargs.append(arg)
	assert input_file
	path, name = os.path.split(input_file)

	scripts, cpp = metapy2tinypypp( open(input_file, 'rb').read().decode('utf-8') )

	if cpp:
		open('./tinypy/__user__.gen.h', 'wb').write(cpp.encode('utf-8'))

	if len(scripts) == 1:
		source = scripts[0]
		tempf = '/tmp/%s_main.py'%name
		open(tempf, 'wb').write(source.encode('utf-8'))
		subprocess.check_call(['./tpc']+exargs+['-o', './%s.bytecode'%name, tempf])
	else:
		for i in range(len(scripts)):
			source = scripts[i]
			tempf = '/tmp/%s_thread%s.py'%(name,i)
			open(tempf, 'wb').write(source.encode('utf-8'))
			subprocess.check_call(['./tpc']+exargs+['-o', './%s_thread%s.bytecode'%(name,i), tempf])

main()

