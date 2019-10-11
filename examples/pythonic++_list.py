with c++:
	@module( mycppmodule )
	def foo(a, o):
		std::cout << a << std::endl
		a.append( "world" )
		a.append( std::string("mystdstring") )
		a.append( o )
		a.append( 1 )
		a.append( 9.5 )
		return None


import mycppmodule
x = ['hello']
b = 'bar'
mycppmodule.foo( x, b )
print( x )

