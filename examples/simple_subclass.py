class Foo:
	def __init__(self, x,y):
		self.x = x
		self.y = y
		
	def get_x(self):
		return self.x

class Bar( Foo ):
	def get_y(self):
		return self.y

def test():
	print('making Foo')
	f = Foo( 1, 'foo')
	print('made Foo')
	print(f)
	print('testing f.x')
	print(f.x)
	print('testing f.get_x()')
	print(f.get_x())
	print('testing f.y')
	print(f.y)
	print('making Bar')
	b = Bar( 10, 'bar')
	print('made Bar')
	print(b)
	print('testing b.x')
	print(b.x)
	print('testing b.get_x()')
	print(b.get_x())
	print('testing b.y')
	print(b.y)
	print('testing b.get_y()')
	print(b.get_y())
	print('OK')

test()
