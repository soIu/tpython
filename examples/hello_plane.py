def test():
	print('hello world')
	normal = vec3(0,1,0)
	length = 2.0
	p = plane( normal, length )
	print(p)
	print(p.normal)
	print(p.length)
	print(p.distance_to( vec3(10,20,30) ))

test()