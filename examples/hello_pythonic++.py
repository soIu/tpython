with c++:
	@module( mycppmodule )
	def foo(a, b, c):
		std::cout << a << std::endl;
		std::cout << b << std::endl;
		std::cout << c << std::endl;
		return None


import mycppmodule
mycppmodule.foo(1, 'hello', 'world')

