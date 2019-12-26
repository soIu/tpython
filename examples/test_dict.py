def test():
	a = {'foo': 'bar'}
	print(a)
	print(a['foo'])
	b = {'x':'y'}
	a.update(b)
	print(a)
	keys = a.keys()
	print(keys)
	vals = a.values()
	print(vals)

test()
