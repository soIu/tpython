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
Pointer types can use `*` or the black rightwards arrow head `⮞`
Pointer objects can use `🠊` instead of `->`

Templates can use regular C++ syntax, `<>` or `≼≽`.
Templates with multiple arguments can be separated with `,` or `⧟`.

