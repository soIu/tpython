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
	f = Foo( 1, 'foo')
	print(f.x)
	print(f.get_x())
	print(f.y)

	b = Bar( 10, 'bar')
	print(b.x)
	print(b.get_x())
	print(b.y)
	print(b.get_y())


test()
