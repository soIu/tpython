with javascript:
	def myfunc(x,y) ->int:
		console.log(x)
		console.log(y)
		return x * y

with c++:
	@javascript
	def call_alert(float n, const char* a, const char *b):
		window.alert( a + b + n)
	@module( mycppmodule )
	def foo(n, a, b):
		call_alert(n, a.as_cstring(), b.as_cstring() )
		int r = myfunc(4, 5)
		print(r)
		return None


import mycppmodule
mycppmodule.foo(99, 'hello', 'world')
