
# TPython Syntax

TPython syntax is the same as Python3 in almost every case.
One exception is in Python3 `@` is used for matrix multiplication, while TPython has no dedicated symbol for this.
In TPython to multiply you simply use `*`, or unicode times `×`, there is no difference.
For better readablity, TPython also supports the unicode division symbol, so to divide you can use either: `/` or `÷`

Another difference is `eval` and `exec` are not allowed in TPython, your scripts must be compiled ahead of time.

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

Options for `rebuild.py`
* `--secure` (turn on extra security features)
* `--secure-binary` (turn on binary security features, scramble function names and load them using `dlsym`)
* `--includeos` (compile standalone bootable exe using IncludeOS)
* `--windows` (compile exe for MS Windows)
* `--arm` (compile exe for ARM)
* `--wasm` (use Emscripten to compile wasm binary)
* `--html` (use Emscripten to compile wasm binary)
* `--android` (compile exe for Android)
* `--sdl` (link to SDL2 and make `sdl` module available)
* `--blendot` (build with Blendot math and object types)
* `--cpython` (link to libpython and allow calling CPython from TPython)
* `--pgo` (compile exe twice, and use profile guided optimizations)
* `--clean` (remove all cached `.o` files)
* `--debug` (turn on extra debugging)
* `--std-malloc` (use standard malloc instead of RPMalloc)
* `--clang` (compile with clang6 instead of gcc)


# Compile TPython Scripts to Bytecode

The TPython++ VM can only read in bytecode, so you need to use python to compile `.bytecode` files.  The example below will write out a `myscript.bytecode` file.
```bash
python tpython++compiler.py myscript.py
```

Options for `tpython++compiler.py`
* `--beta` (use experimental beta features, faster but could be unstable)
* `--debug` (turn on extra debugging)

To embed bytecode directly into the interpreter exe, pass the name of your script to `rebuild.py`
```bash
./rebuild.py myscript.py
```
This is more secure, and will compile an interpreter that will only run the embedded bytecode.


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
* to enable you must pass the option `--cpython` to `rebuild.py`

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

# Compile as Shared Library

To compile the tpython as a shared library run:

Linux (makes libtpython++.so)
```bash
./rebuild.py --clean --shared
```

Windows (makes libtpython++.dll)
```bash
./rebuild.py --clean --shared --windows
```

The function `tpython_run` is exported with `C` linkage so it can be called from other exes
Python and ctypes example:
```python
import ctypes
tpylib = ctypes.cdll.LoadLibrary('./libtpython++.so')
data = open('my.bytecode').read()
func = tpylib.tpython_run
func( data, len(data) )
```

# WASM and Javascript Support

The interpreter can be compiled with an embedded script like this:
```bash
./rebuild.py --html myscript.py
```
This requires you have installed Emscripten, afterward you should have: tpython++.html (100K), tpython++.js (260K), and tpython++.wasm (560K).  You can directly open tpython++.html in a browser for testing, it will load the js and wasm files.

Mixing both WASM and Javascript can be complex, to make it simpler TPython custom syntax that generates the required Emscripten API calls.

```python
with javascript:
	console.log('hello world')

foo = javascript("1+1", returns='int')

```
Using `with javascript:` syntax allows you to insert multiple lines of javascript to be run as soon as the TPython interpreter runs.
To run a single line of Javascript directly, use the function `javascript(..., returns='TYPE')`, where type should be of: void, int, float, or double.

Inside a `with javascript:` block, you can also define Javascript functions that look like Python functions,
these functions are then callable from Python as regular functions (note only one per-line, no nesting allowed)

```python
with javascript:
	def myfunc(x,y) ->int:
		return x+y

n = myfunc(1,1)

```
Above is an example of how to capture values from Javascript into the TPython interpreter.
To get values from Javascript in Pythonic++ code that is fully compiled to WASM, use the `@javascript` decorator.

```python
with c++:
	@javascript
	def call_alert(float n, const char* a, const char *b):
		window.alert( a + b + n)
	@module( mycppmodule )
	def foo(n, a, b):
		call_alert(n, a, b)
		return None


import mycppmodule
mycppmodule.foo(99, 'hello', 'world')
```

# Blendot Types

Blendot is a hard fork of the Godot game engine. The Blendot rewrite replaces C++ with Pythonic++, and GDScript with TPython.
TPython can be built with the minimal core types of Blendot by passing `--blendot` option to `rebuild.py`, and provides the following types:
* vec2
* vec3
* quat
* color
* rect
* tri
* plane
* aabb
* mat3
* transform
* RID
* spatial
* mesh


# Old Benchmarks and Articles

https://medium.com/@judge_raptor/the-smallest-fastest-python-ever-827a36390fbf

https://medium.com/@judge_raptor/tpython-with-c-abc90e32d760

https://medium.com/@judge_raptor/pythonic-2869545fcad6

https://medium.com/@judge_raptor/tpythonos-a959ec82793a

https://medium.com/@judge_raptor/the-smallest-fastest-most-secure-python-ever-5fe2e33ce8cd

https://medium.com/@judge_raptor/the-first-high-performance-game-engine-written-in-python-a2be13ff34f2

https://medium.com/@judge_raptor/c-6e89c6bbc8f0
