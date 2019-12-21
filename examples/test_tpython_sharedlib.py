#!/usr/bin/python
import ctypes, subprocess

tpylib = ctypes.cdll.LoadLibrary('../libtpython++.so')
print(tpylib)

subprocess.check_call(['./tpython++compiler.py', 'examples/hello_world.py'], cwd='..')

data = open('../hello_world.py.bytecode').read()
print('tpython bytecode:')
print(data)

func = tpylib.tpython_run
print(func)
func( data, len(data) )
