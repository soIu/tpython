def get_x():
	return x

mylookup = {
	'bar': 'BAR'
}

class Foo:
	def __init__(self, x,y):
		global x,y
		x = x
		y = y

	def __getitem__(self, attr_name):
		print('trying to get some attr named:', attr_name)
		if attr_name == 'get_x':
			return get_x
		elif attr_name == 'x':
			return x
		elif attr_name == 'y':
			return y
		elif attr_name == 'z':
			return 99
		else:
			return mylookup[attr_name]
			

def test():
	f = Foo( 1, 'foo')
	print(f.x)
	print(f.get_x())
	print(f.y)
	print(f.z)
	print(f.bar)


test()
