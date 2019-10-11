with c++:
	class Foo:
		def __init__(self, x, y ):
			self.x = x
			self.y = y
		def bar(self, TP):
			return tp_number(self.x.number.val + self.y.number.val)
	@module( mycppmodule )
	def new_foo(a, b):
		std::cout << "making new foo from c++" << std::endl
		auto f = Foo(a,b)
		tp_set(tp, f, tp_string_atom(tp, "bar"), tp_function(tp,&f.bar))
		return f


import mycppmodule
foo = mycppmodule.new_foo( 400, 20 )
print('made new foo')
print( foo )
res = foo.bar()
print( res )

