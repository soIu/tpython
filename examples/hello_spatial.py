def test():
	print('hello world')
	pos = vec3(0,0,0)
	rot = vec3(0,0,90)  ## degrees, not radians
	scl = vec3(1,1,1)
	s = spatial(pos, rot, scl)
	print(s)
	s.set_position( vec3(1,2,3) )
	s.set_rotation( vec3(90,180,45) )
	s.set_scale( vec3(10,10,10) )
	print(s.position)
	print(s.rotation)
	print(s.scale)
	del s

test()