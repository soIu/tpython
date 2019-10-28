def test():
	print('hello world')
	v = quat(1.1, 2.2, 3.3, 4.4)
	print(v)
	print(v.x)
	print(v.y)
	print(v.z)
	print(v.w)
	v.x = 99
	print(v.x)
	v.y += 400
	print(v.y)
	print(v.length())
	v2 = v.normalized()
	print(v2)
	v3 = v + v2
	print(v3)

test()