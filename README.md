# tpythonpp

A tiny GIL-less python implementation (based on TinyPy), written in Pythonic++ (a dialect of C++), and optimized for speed and portability to mobile platforms.
TPython++ is used by the Blendot game engine.  http://blendot.org

# Benchmarks

![alt text](https://miro.medium.com/max/1164/1*SWL51u0qro4N6_peZOxu5w.png "Pystone Benchmark")

![alt text](https://miro.medium.com/max/1164/1*Q0XjKb6OiGNo99--TtxjKA.png "Richards Benchmark")

# Ahead of Time Compiled Python

![alt text](https://miro.medium.com/max/1164/1*LOxJcL6TUsa8ZAwPfj4meg.png "Richards Benchmark AOT")

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


# New Articles

https://medium.com/@judge_raptor/2x-faster-than-python-7c15ab0a9286

https://medium.com/@judge_raptor/77x-faster-than-rustpython-f8331c46aea1

https://medium.com/@judge_raptor/aotpy-52x-faster-than-python-2bda98ab5e57
