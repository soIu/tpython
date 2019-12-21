with c++:
	@javascript
	def call_alert(float n, const char* a, const char *b):
		window.alert( a + b + n)
	@module( mycppmodule )
	def foo(n, a, b):
		print(n)
		print(a)
		print(b)
		call_alert(n, a, b)
		return None


import mycppmodule
mycppmodule.foo(99, 'hello', 'world')

