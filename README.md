# tpythonpp

A tiny GIL-less python implementation (based on TinyPy), fully upgraded from C to C++11, and optimized for speed and portability to mobile platforms.
TPython++ is used by the Blendot game engine.  http://blendot.org

# roadmap

* optionally embed CPython (libpython) and support calling classic python using new syntax `with python:`
* preparser to generate better optimized output and bytecodes
* new bytecodes to speed up the interpreter
* new python3 style type hints, and new bytecodes to optimize them
* remove the bootstrapping and self hosting, we can compile bytecodes best from classic python.
* allow users to easily extend the interpreter loop with their own custom C++ classes
* restrict python syntax and rules to speed up the interpreter
* replace the Makefile with scons

# history

TinyPy is the smallest Python implementation ever, just 64K, created by Phil Hassey in 2008.  TPython++ is based on RainWoodMans fork of TinyPy. https://github.com/rainwoodman/tinypy

# Optional CPython

CPython3.7 can be used from within TPython++ scripts using this syntax:
```python
import python
with python:
	print('hello world from CPython')
	import sys
	print(sys.version)

```
You can also call `python.run(string)` directly like this:
```python
import python
python.run("print('hello world')")
```
TODO: expose `python.eval(string)` which will return a wrapped `PyObject*` object. 

CPython Notes:
* using CPython on mobile platforms will not work
* libpython3.7m.so must be available on your system

# Multi-threading

TPython++ supports GIL-free multi-threading, the syntax is:
```python
with thread:
	foo()
	bar()
with thread:
	foo()
	bar()
```
The above example generate two `.bytecode` files, one for each thread, and you need to pass both of them on the command line to the `tpython++` executeable, like this:
```bash
./tpython++ myscript_thread0.bytecode myscript_thread1.bytecode
```

# Benchmarks

You can see TPython++ vs Python vs PyPy vs GDscript benchmarks at:
http://blendot.org/tpython/