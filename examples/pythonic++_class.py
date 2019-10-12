#std::function<tp_obj(tp_vm*)> fn = [=](tp_vm *tp){return fptr->bar(tp);};
#tp_set(tp, f, tp_string_atom(tp, "bar"), tp_function(tp, fn))

with c++:
	class Foo:
		def add(self, u, v):
			std::cout << "calling add" << std::endl
			return tp_number(u.number.val + v.number.val)
		def bar(self):
			std::cout << "calling bar" << std::endl
			std::cout << self.x << std::endl
			std::cout << self.y << std::endl
			return tp_number(self.x.number.val + self.y.number.val)
		def __init__(self, x, y ):
			self.x = x
			self.y = y
	@module( mycppmodule )
	def new_foo(a, b):
		std::cout << "making new foo from c++" << std::endl
		Foo *fptr = new Foo(tp, a,b)
		auto f = *fptr
		std::cout << f.x << std::endl
		std::cout << f.y << std::endl
		return f


import mycppmodule
foo = mycppmodule.new_foo( 400, 20 )
print('made new foo')
print( foo )
res = foo.bar()
print( res )
print( foo.add(1,99) )

