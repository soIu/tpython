class Foo:
	def __init__(self, x,y):
		self.x = x
		self.y = y
		
	def get_x(self):
		return self.x
	def get_y(self):
		return self.y

class Bar(object):
	def bar(self):
		return 1

def test():
	f = Foo( 1, 'hello world')
	print(f.x)
	print(f.get_x())
	print(f.y)
	print(f.get_y())

	print('testing Bar')
	b = Bar()
	assert b.bar()==1

test()
