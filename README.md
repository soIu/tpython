# tpythonpp

A tiny GIL-less python implementation (based on TinyPy), written in Pythonic++ (a dialect of C++), and optimized for speed and portability to mobile platforms.
TPython++ is used by the Blendot game engine.  http://blendot.org

# history

TinyPy is the smallest Python implementation ever, just 64K, created by Phil Hassey in 2008.  TPython++ is based on RainWoodMans fork of TinyPy. https://github.com/rainwoodman/tinypy

# TPython Syntax

TPython syntax is the same as Python3 in almost every case.
One exception is in Python3 `@` is used for matrix multiplication, while TPython has no dedicated symbol for this.
In TPython to multiply you simply use `*`, or unicode times `×`, there is no difference.
For better readablity, TPython also supports the unicode division symbol, so to divide you can use either: `/` or `÷`

Another difference is `eval` and `exec` are not allowed in TPython, your scripts must be compiled ahead of time.

# Blendot Types

Blendot is a hard fork of the Godot game engine. The Blendot rewrite replaces C++ with Pythonic++, and GDScript with TPython.
By default TPython is built with the minimal core types of Blendot, and provides the following types:
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

If you do not need these types, you can pass the option `--no-blendot` to `rebuild.py`

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
* `--android` (compile exe for Android)
* `--sdl` (link to SDL2 and make `sdl` module available)
* `--no-blendot` (do not build with Blendot math and object types)
* `--cpython` (link to libpython and allow calling CPython from TPython)
* `--pgo` (compile exe twice, and use profile guided optimizations)
* `--clean` (remove all cached `.o` files)
* `--debug` (turn on extra debugging)


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

# Pythonic++

Pythonic++ is our own dialect of C++ that adopts the style of Python syntax,
it is a minimal translator and binding generator, that will not get in your way when doing direct C++.
The TPython interpreter is itself written in Pythonic++, and the Pythonic++ translator is itself written in Python.
Pythonic++ files end with: `.pyc++` or `.pyh`, and when translated, they become: `.gen.cpp` and `.gen.h`
The recommended code editor for Pythonic++ files is our custom fork of Gedit.
https://gitlab.com/hartsantler/gedit

# Pythonic++ Syntax

To get started writting Pythonic++ programs, you should already know Python, and the basic rules of C++.
Unlike regular C++, Pythonic++ is very white space strict, and you must use tabs by default, 
using tabs will automatically insert closing and ending braces `{}` where needed.  
When you need to bypass auto-bracing, you can use spaces to indent.

For each line a semicolon `;` is inserted when needed, this works in most cases, but not all the time.
One example is with a brace initialized struct `auto foo = {bar}`, 
this case fails because `;` are not inserted when the line ends with `}`, so instead write `auto foo = {bar};`, or `auto foo = bar()`

Python style `if/elif/else` is used just like regular Python, except that C++ logical booleans must be used instead of the Python keywords: `and`, `or`, `not`, so instead use: `&&`, `||`, `!`.  Two special cases are `if not` and `elif not`, these forms are allowed.

For loops in Pythonic++ are not Python style (yet), and instead follow C++ rules, except for ending with a colon.
The syntax is `for (int i=0; i<N; i++):`

Comments can start with `//`, or begin with `/*` and end with `*/`, or start with `##`.
Note that lines that begin with a single `#` are considered a macro, or some type of special directive for the C-pre-processor.

To define a macro, you can use C++ style: `#define foo bar`, this is allowed, but bad style.
It is better to define your macros using Python style: `define(foo=bar)`.  To undefine a macro, use `undef(foo)`
When you need to define a multi-line macro, you can use this syntax:
```
define foo:
	bar
	...
```
Note that when you define a multi-line macro, the translator will not alter the code in that block, except for adding backslash to each line.  So you have to manually apply braces and semi-colons where needed.

Pythonic++ functions begin with `def`, just like in regular Python, and end with `-> return_type:` when the function returns non-void.
For static functions use the `@static` decorator, and for const functions use the `@const` decorator.
Function arguments should be typed, if they are not, then their type will default to `auto` which requires a C++14 compilier.
Use C++ style to type your arguments, where the type is given first: `def foo(int a, double b):`
C++11 lambda functions are defined like this: `auto myfunc = def[]():`, the square brackets following `def` are the capture list.
Blank lines are not allowed in function bodies.

Inside functions you can use the `goto` statement to jump to a block of code.  The syntax to do a `goto` jump is simply `goto mylabel`.
To define a new `goto` code block use:
```
goto mylabel:
	foo
	bar
```

To import an local header file, you can use either: `#include "myheader.h"` or `import "myheader.h"`.
Importing external headers from the system can be done using: `import <someheader>`.
Note if your header is written in Pythonic++, as a `.pyh` file, then you will import it as: `import "myheader.gen.h"`

References can use standard C++ syntax `&`, or with the curved upwards arrow `⤴`.
Pointers can use `*` or the black rightwards arrow head `⮞`

Templates can use regular C++ syntax, `<>` or `≼≽`.
Templates with multiple arguments can be separated with `,` or `⧟`.

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

# Benchmarks and Articles

https://medium.com/@judge_raptor/the-smallest-fastest-python-ever-827a36390fbf

https://medium.com/@judge_raptor/tpython-with-c-abc90e32d760

https://medium.com/@judge_raptor/pythonic-2869545fcad6

https://medium.com/@judge_raptor/tpythonos-a959ec82793a

https://medium.com/@judge_raptor/the-smallest-fastest-most-secure-python-ever-5fe2e33ce8cd

https://medium.com/@judge_raptor/the-first-high-performance-game-engine-written-in-python-a2be13ff34f2

https://medium.com/@judge_raptor/c-6e89c6bbc8f0
