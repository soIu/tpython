import sdl

SW = 800
SH = 240

def test():
	w = world()
	print('world:', w)
	s = space()
	print('space:', s)
	w.setGravity( vec3(0,-9.81,0) )
	floor = geomPlane(s, vec3(0,1,0), -200)
	print('floor:', floor)
	leftwall = geomPlane(s, vec3(1,0,0), 0)
	rightwall = geomPlane(s, vec3(-1,0,0), -800)
	b = body( w )
	m = mass()
	#m.setSphere( 2500.0, 0.05 )  ## so heavy that default contact joints will fail
	m.setSphere( 0.5, 2.5 )
	b.setMass( m )
	geo = geomBox(s, vec3(5,5,5) )
	print('box:', geo)
	geo.setBody(b)
	b.setPosition( vec3(SW/2,20,0) )
	time = 0.0
	dt = 0.3
	while True:
		sdl.clear( [0,0,0] )
		for e in sdl.poll():
			if e.type == "KEYDOWN":
				print('key:', e.key)
				if e.key == 80:    ## left key
					b.addForce( vec3(-50,0,0) )
				elif e.key == 79:  ## right key
					b.addForce( vec3(50,0,0) )
				elif e.key == 81: ## down key
					b.addForce( vec3(0,-20,0) )
			elif e.type == "KEYUP":
				if e.key == 82: ## up key
					b.addForce( vec3(0,10,0) )
				elif e.key == 44:    ## space key
					b.addForce( vec3(0,100,0) )
		s.spaceCollide()
		w.step(dt)
		v = b.getPosition()
		x = v[0]
		y = v[1]
		sdl.draw([x,-y, 10,10], [255,0,0] )
		sdl.draw([0,220, SW,10], [5,200,0] )
		sdl.flip()
		time += dt
		sdl.delay(30)

def main():
	sdl.initialize()
	sdl.window( (SW,SH) )
	test()

main()
