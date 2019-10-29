def test():
	print('hello world')
	c = color(1,0.2,0.2, 1)
	print(c)
	print(c.r)
	print(c.g)
	print(c.b)
	print(c.a)
	c.a = 0.5
	print(c.a)
	c.b += 0.1
	print(c.b)
	d = c.darkened( 0.9 )
	print(d)

test()