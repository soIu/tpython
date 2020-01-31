with c++:
	class MyClass:
		def __init__(self):
			self.x = None
			self.y = None
			self.z = None
		def mymethod(self):
			raise NotImplementedError
		def dispatch(self):
			return self.mymethod()
	class Foo(MyClass):
		def __init__(self):
			MyClass.__init__(self)
		def mymethod(self):
			return self.x
	class Bar(MyClass):
		def __init__(self):
			MyClass.__init__(self)
		def mymethod(self):
			return self.y
	def test1():
		f = Foo()
		b = Bar()
		f.x = 1
		b.y = 2
		print( f.x )
		print( b.y )
		print( f.dispatch() )
		if int( f.dispatch()) != 1:
			raise RuntimeError
		print("f.dispatch() OK")
		if int( b.dispatch()) != 2:
			raise RuntimeError
		print("b.dispatch() OK")
	@module( my_cpp_module )
	def test_subclasses():
		test1()
		return 1

import my_cpp_module

def main():
	assert my_cpp_module.test_subclasses()
	print('OK')
		
main()
