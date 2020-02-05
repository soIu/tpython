def test():
	w = world()
	print(w)
	w.setGravity( vec3(0,-9.81,0) )
	b = body( w )
	m = mass()
	m.setSphere( 2500.0, 0.05 )
	b.setMass( m )
	b.setPosition( vec3(0,2,0) )
	b.addForce( vec3(0, 200, 0) )
	b.addTorque( vec3(10,0,0) )
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
		q = b.getRotation()
		print(q)
		print('linear vel:')
		vel = b.getLinearVel()
		print( vel )
		print('angular vel:')
		avel = b.getAngularVel()
		print( avel )
		time += dt
	q2 = quat(1,2,3,4)
	print(q2)

def main():
	test()

main()
