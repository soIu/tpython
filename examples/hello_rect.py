def test():
	print('hello world')
	r = rect(0,0, 320, 240)
	print(r)
	print(r.x)
	print(r.y)
	print(r.width)
	print(r.height)
	r.x = 2
	print(r.x)
	r.y += 0.1
	print(r.y)
	area = r.get_area()
	print(area)

test()