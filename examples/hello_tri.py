def test():
	print('hello world')
	a = vec3(-1,0,0)
	b = vec3(0,1,0)
	c = vec3(1,0,0)
	t = tri(a,b,c)
	print(t)
	t.a = vec3(-9, -1, 0)
	print(t)
	print(t.a)

test()