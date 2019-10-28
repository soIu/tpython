def test():
	print('hello world')
	v = vec2(1.1, 2.2)
	print(v)
	print(v.x)
	print(v.y)
	v.x = 99
	print(v.x)
	v.y += 400
	print(v.y)

test()