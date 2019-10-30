def test():
	print('hello world')
	m1 = mat3(
		vec3(1,0,0),
		vec3(0,1,0),
		vec3(0,0,1),
	)
	print(m1)
	m2 = mat3(
		vec3(10,20,30),
		vec3(0.1,10 ÷ 2,0.3),
		vec3(0.5,0.5,10),
	)
	m3 = m1 * m2
	print(m3)
	m4 = m3 × m3
	print(m4)

test()