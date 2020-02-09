import sdl

SW = 800
SH = 240

def test():
	w = world()
	print(w)
	w.setGravity( vec3(0,-9.81,0) )
	b = body( w )
	m = mass()
	m.setSphere( 2500.0, 0.05 )
	b.setMass( m )
	b.setPosition( vec3(SW/2,20,0) )
	b.addTorque( vec3(10,0,0) )
	b.setRotation( quat(0.5, 0.5, 0, 0) )
	time = 0.0
	dt = 0.3
	while True:
		sdl.clear( vec3(0,0,0) )
		for e in sdl.poll():
			if e["type"] == "KEYDOWN":
				print("key:", e["key"])
				if e["key"] == 80 or e["key"] == 113:    ## left key
					b.addForce( vec3(-50,0,0) )
				elif e["key"] == 79 or e["key"] == 114:  ## right key
					b.addForce( vec3(50,0,0) )
		w.step(dt)
		v = b.getPosition()
		if v[1] < -200:
			b.addForce( vec3(0,200,0) )
		x = v[0]
		y = v[1]
		sdl.draw( vec4(x,-int(y), 10,10), vec3(255,0,0) )
		sdl.draw( vec4(0,220, SW,10), vec3(5,200,0) )
		sdl.flip()
		time += dt
		sdl.delay(30)

def main():
	sdl.initialize()
	sdl.window( vec2(SW,SH) )
	test()

main()
