with c++:
	@module( mycppmodule )
	def foo(a, b, c):
		print(a)
		print(b)
		print(c)
		return None


import mycppmodule
mycppmodule.foo(1, 'hello', 'world')

