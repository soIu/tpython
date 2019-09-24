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

# history

TinyPy is the smallest Python implementation ever, just 64K, created by Phil Hassey in 2008.  TPython++ is based on RainWoodMans fork of TinyPy. https://github.com/rainwoodman/tinypy
