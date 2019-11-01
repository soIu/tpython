def test():
	print('hello world')
	m = mat3(
		vec3(1,0,0),
		vec3(0,1,0),
		vec3(0,0,1),
	)
	pos = vec3(10,20,30)
	t = trans(m, pos)
	print(t)

test()