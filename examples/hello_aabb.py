def test():
	print('hello world')
	a = aabb(
		vec3(1,1,1),
		vec3(10,20,20),
	)
	print(a)
	print(a.position)
	print(a.size)
	b = aabb(
		vec3(1,1,1),
		vec3(100,200,200),
	)
	c = a.merge(b)
	print(c)

test()