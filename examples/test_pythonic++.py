with c++:
	MyGlobal = 10
	@module( my_cpp_module )
	def test_myglobal(n):
		global MyGlobal
		MyGlobal += int(n)
		return MyGlobal
	class MyClass:
		def __init__(self):
			self.x = 1
			self.y = None
			self.z = 2
		def is_x_and_y(self):
			return self.x and self.y
	G = MyClass()
	@module( my_cpp_module )
	def test_myclass(n):
		G.x += int(n)
		print("G.x=", G.x)
		return G.x
	@module( my_cpp_module )
	def test_myclass_sety(ob):
		G.y = ob
		print("G.y=", G.y)
		return G.y
	@module( my_cpp_module )
	def test_myclass_isxy():
		return G.is_x_and_y()
	@module( my_cpp_module )
	def test_myclass_isnotxy():
		# in regular python the extra (not ...) is not required
		if (not G.x) and (not G.y):
			return True
		else:
			return False
	
import my_cpp_module

def main():
	print('testing myglobal += n')
	assert my_cpp_module.test_myglobal(1) == 11
	assert my_cpp_module.test_myclass(1) == 2

	a = 'hello'
	assert my_cpp_module.test_myclass_sety(a) == a

	my_cpp_module.test_myclass_sety(False)
	assert my_cpp_module.test_myclass_isxy() == False

	my_cpp_module.test_myclass_sety(1)
	assert my_cpp_module.test_myclass_isxy() == True

	assert my_cpp_module.test_myclass_isnotxy() == False

	print('OK')
	
	
main()
