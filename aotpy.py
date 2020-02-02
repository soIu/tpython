#!/usr/bin/python
import os, sys, subprocess

# always generate code relative to this file.
workspace_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(workspace_dir)

fname = None
fpath = None
for arg in sys.argv[1:]:
	if arg.endswith('.py'):
		fpath = arg
		fname = os.path.split(fpath)[-1]
		break

assert fname

if '--wasm' in sys.argv or '--html' in sys.argv:
	subprocess.check_call( [ './rebuild.py', '--html', '--aot', fpath ] )
	print('saving exe to:')
	subprocess.check_call( [ 'cp', '-v', './%s.wasm.gz' % fname , '/tmp/%s.wasm.gz'  % fname ] )
	subprocess.check_call( [ 'cp', '-v', './%s.js'      % fname, '/tmp/%s.js'        % fname ] )
	subprocess.check_call( [ 'cp', '-v', './%s.html'    % fname, '/tmp/%s.html'      % fname ] )

elif '--gcc' in sys.argv:
	subprocess.check_call( [ './rebuild.py', '--pgo', '--aot', fpath ] )
	print('saving exe to:')
	subprocess.check_call( [ 'cp', '-v', './tpython++', '/tmp/%s.bin'  % fname ] )

else:
	subprocess.check_call( [ './rebuild.py', '--clang', '--pgo', '--aot', fpath ] )
	print('saving exe to:')
	subprocess.check_call( [ 'cp', '-v', './tpython++', '/tmp/%s.bin'  % fname ] )

