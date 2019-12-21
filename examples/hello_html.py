with c++:
	import <emscripten.h>
	@javascript
	def call_alert():
		window.alert('hello js world')
	@module( mycppmodule )
	def foo(a, b):
		print(a)
		print(b)
		call_alert()
		return None


import mycppmodule
mycppmodule.foo('hello', 'world')

