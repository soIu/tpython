#std::function<tp_obj(tp_vm*)> fn = [=](tp_vm *tp){return fptr->bar(tp);};
#tp_set(tp, f, tp_string_atom(tp, "bar"), tp_function(tp, fn))

with c++:
	class Foo(object):
		def add(self, u, v):
			print("calling add")
			return u + v
		def sub(self, u, v):
			return u - v
		def mul(self, u, v):
			return u * v
		def div(self, u, v):
			return u / v
		def bar(self):
			print("calling bar")
			print(self.x)
			print(self.y)
			return self.x + self.y
		def __init__(self, int x, int y ):
			self.x = x
			self.y = y
	@module( mycppmodule )
	def new_foo(a, b):
		print("making new foo from c++")
		fptr = Foo(a,b)
		return fptr


import mycppmodule
foo = mycppmodule.new_foo( 400, 20 )
print('made new foo')
print( foo )
res = foo.bar()
print( res )
print( foo.add(1,99) )
print( foo.sub(1,99) )
print( foo.mul(2,99) )
print( foo.div(1,99) )

