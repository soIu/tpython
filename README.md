# tpythonpp

A tiny GIL-less python implementation (based on TinyPy), written in Pythonic++ (a dialect of C++), and optimized for speed and portability to mobile platforms.
TPython++ is used by the Blendot game engine.  http://blendot.org

# history

TinyPy is the smallest Python implementation ever, just 64K, created by Phil Hassey in 2008.  TPython++ is based on RainWoodMans fork of TinyPy. https://github.com/rainwoodman/tinypy

# Compile TPython++

Use the helper script `rebuild.py` to compile for your target platform,
it will generate a `Makefile` and run the build for you.


How to build and test for ARM
```bash
./rebuild.py --arm
qemu-arm tpython++.arm myscript.bytecode
```

How to build and test for Windows
```bash
./rebuild.py --windows
wine64 ./tpython++.exe myscript.bytecode
```

How to build and test for Linux
```bash
./rebuild.py
./tpython++ myscript.bytecode
```

# Compile TPython Scripts to Bytecode

The TPython++ VM can only read in bytecode, so you need to use python to compile `.bytecode` files.  The example below will write out a `myscript.bytecode` file.
```bash
python tpython++compiler.py myscript.py
```

Options for `tpython++compiler.py`
* `--beta` (use experimental beta features, faster but could be unstable)


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
* using CPython on ARM or Windows platforms will not work
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

# Pythonic++

Pythonic++ is our own dialect of C++ that adopts the style of Python syntax,
it is a minimal translator and binding generator, that will not get in your way when doing direct C++.
For maximum speed and readability, nothing beats Pythonic++.  
The best way to learn Pythonic++ is to read the TPython interpreter source code, it is fully
written in Pythonic++, the file extensions are: `.pyc++` and `.pyh`

# Benchmarks and Articles

https://medium.com/@judge_raptor/the-smallest-fastest-python-ever-827a36390fbf

https://medium.com/@judge_raptor/tpython-with-c-abc90e32d760

https://medium.com/@judge_raptor/pythonic-2869545fcad6