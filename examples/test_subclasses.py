class Foo:
	def __init__(self, x,y):
		self.x = x
		self.y = y
		
	def get_x(self):
		return self.x

	def getY(self):
		raise NotImplementedError
		
	def get_y(self):
		return self.getY()

class Bar(Foo):
	def __init__(self,x,y):
		Foo.__init__(self,x,y)
		
	def getX(self):
		return self.get_x()

	def getY(self):
		return self.y

def test():
	print('testing Bar subclass')
	b = Bar(100, 200)
	print(b.x)
	assert b.x == 100
	print(b.y)
	assert b.y == 200
	print('testing b.get_x()')
	assert b.get_x()==100
	assert b.getX()==100
	assert b.get_y()==200

test()
