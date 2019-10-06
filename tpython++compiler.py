#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys, subprocess

def metapy2tinypypp( source ):
	shared = []
	right_side = []
	thread_local = []
	thread = None
	cpy = None
	for ln in source.splitlines():
		if u'┃' in ln:
			assert ln.count(u'┃')==1
			a,b = ln.split(u'┃')
			shared.append(a)
			right_side.append(b)
		elif ln.startswith('with python:'):
			cpy = []
		elif ln.startswith('with thread:'):
			thread = []
			thread_local.append(thread)
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

	return scripts

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
	scripts = metapy2tinypypp( open(input_file, 'rb').read().decode('utf-8') )
	if len(scripts) == 1:
		source = scripts[0]
		tempf = '/tmp/%s_main.py'%name
		open(tempf, 'wb').write(source)
		subprocess.check_call(['./tpc']+exargs+['-o', './%s.bytecode'%name, tempf])
	else:
		for i in range(len(scripts)):
			source = scripts[i]
			tempf = '/tmp/%s_thread%s.py'%(name,i)
			open(tempf, 'wb').write(source)
			subprocess.check_call(['./tpc']+exargs+['-o', './%s_thread%s.bytecode'%(name,i), tempf])

main()

