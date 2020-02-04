def test():
	w = world()
	print(w)
	w.setGravity(0, -9.81, 0)
	b = body( w )
	m = mass()
	m.setSphere( 2500.0, 0.05)
	b.setMass( m )
	b.setPosition( 0, 2, 0 )
	b.addForce( vec3(0, 200, 0) )
	time = 0.0
	dt = 0.04
	while time < 2.0:
		print('simulating....')
		w.step(dt)
		v = b.getPosition()
		print(v)
		if v[1] < 0.0:
			print("hit ground")
			b.addForce( vec3(0,1000,0) )
		time += dt

def main():
	test()

main()
