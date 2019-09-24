#!/usr/bin/python
import os, sys, subprocess

def metapy2tinypypp( source ):
	if 'with thread:' not in source:
		return [source]
	shared = []
	thread_local = []
	thread = None
	for ln in source.splitlines():
		if ln.startswith('with thread:'):
			thread = []
			thread_local.append(thread)
		elif thread is not None:
			if ln.startswith('\t'):
				thread.append( ln[1:] )
			else:
				thread = None
		else:
			shared.append(ln)

	scripts = []
	for thread_code in thread_local:
		script = '\n'.join(shared)
		script += '\n'
		script += '\n'.join(thread_code)
		scripts.append(script)

	return scripts

def main():
	assert sys.argv[-1].endswith('.py')
	path, name = os.path.split(sys.argv[-1])
	scripts = metapy2tinypypp( open(sys.argv[-1], 'rb').read() )
	if len(scripts) == 1:
		subprocess.check_call(['./tpc', '-o', './%s.bytecode'%name, sys.argv[-1]])
	else:
		for i in range(len(scripts)):
			source = scripts[i]
			tempf = '/tmp/%s_thread%s.py'%(name,i)
			open(tempf, 'wb').write(source)
			subprocess.check_call([
				'./tpc', '-o', 
				'./%s_thread%s.bytecode'%(name,i), 
				tempf
			])

main()

