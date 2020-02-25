# tpythonpp

A tiny GIL-less python implementation (based on TinyPy), written in Pythonic++ (a dialect of C++), and optimized for speed and portability to mobile platforms.
TPython++ is used by the Blendot game engine.  http://blendot.org

Follow me on Twitter: https://twitter.com/DJRaptor11

# Benchmarks

![alt text](https://miro.medium.com/max/1164/1*SWL51u0qro4N6_peZOxu5w.png "Pystone Benchmark")

![alt text](https://miro.medium.com/max/1164/1*Q0XjKb6OiGNo99--TtxjKA.png "Richards Benchmark")

# Ahead of Time Compiled Python

![alt text](https://miro.medium.com/max/1164/1*LOxJcL6TUsa8ZAwPfj4meg.png "Richards Benchmark AOT")

# AOTPY

Ahead of time compiled Python must follow strict rules inorder to be conformant
for automatic translation to C++.  These rules include:
* each dictionary can only contain a single key type, either: a single char (in single quotes),
   or a string (in double quotes), or a number.  A dictionary will become `std::unordered_map<T,tp_obj>`.
* lists are faster when they only contain a single type, a list of strings will become `std::vector<std::string>`
* sets can only contain numbers or strings.
* functions and methods must be defined in their dependency order, if function B requires function A, then A must be defined first.
* when the translator fails to determine the type of a variable for automatic unwrapping, you must use the `@unwrap(foo=TYPE)` decorator to define the variable type.
* when interfacing with C++, and automatic templates fail to compile, you can type your variables using the `@typedef(foo=TYPE)` decorator.
* classes are automatically exposed to non-AOT code, to call a method on an AOT class, you must define that method before the `__init__` constructor.
* AOT class instances are not garbage collected, you must manually delete them when no longer used.
* a single letter in single quotes is a `char` type, double quoted strings are `const char*`
* white space matters, use tabs for normal indentation, and when the parser fails, adding a space in and around function calls can fix the problem
* lines that end with `;` are considered to be raw C++, and the parser will perform less translation magic on them.
* by default all members of a class are of the type `tp_obj`, which is a union of the interpreter types,
   if you need to store a pointer to an external C++ object, you must cast it to `(void*)` when you assign it to the member.
* a wrapped pointer to an external C++ object can be unwrapped using the `unwrap(T,ob)` macro.
* functions that do not define a return type, will have `tp_obj` as their return type, by default returning `None`

# aotpy.py

Front end build script `aotpy.py` will try to ahead of time compile your python script,
otherwise it will fallback to compiling just bytecode.


example:
```
cd tpythonpp
./aotpy.py benchmarks/recursive_fib.py 
```

# History

TinyPy is the smallest Python implementation ever, just 64K, created by Phil Hassey in 2008.  TPython++ is based on RainWoodMans fork of TinyPy. https://github.com/rainwoodman/tinypy
The AOT translator is based on a higher level form of Pythonic++ syntax.  The TPython interpreter itself is written in low level Pythonic++

# New Articles

https://medium.com/@judge_raptor/2x-faster-than-python-7c15ab0a9286

https://medium.com/@judge_raptor/77x-faster-than-rustpython-f8331c46aea1

https://medium.com/@judge_raptor/aotpy-52x-faster-than-python-2bda98ab5e57

https://medium.com/@judge_raptor/escaping-the-interpreter-5675dfda15d3

https://dev.to/djraptor11/blender-destructive-physics-19o4

https://dev.to/djraptor11/zero-hardcoded-values-2c9j

