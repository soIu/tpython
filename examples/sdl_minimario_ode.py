import sdl
import random
Mario = ['     RRRRR      ','    RRRRRRRRR   ','    HHH--X-     ','   H-H---X---   ','   H-HH---0---- ','   HH----00000  ','     --------   ','  RRRRBBRRR     ','--RRRRBBBRRRR---','--- RRBYBBBBRR--','-- BBBBBBBBBB   ','  BBBBBBBBBBBB  ',' BBBBB    BBBB  ','HHBBB      BBB  ','HHHH       HHHH ',' HHHHH     HHHHH' ]

MarioReversed = [ s.reverse() for s in Mario ]
MarioPal = { 'R':vec3(255,0,0), 'H':vec3(80,50,5), '-':vec3(160,150,100), 'B':vec3(0,0,255), 'Y':vec3(255,255,0), '0':vec3(5,5,5) }

def draw_mario(vec, mario, crouching, running, blink ):
	ox = vec[0]
	oy = -(vec[1]+32)
	y = oy
	Y = 0
	if crouching == True:
		y += 8
	flip_legs = False
	if running==True and random.random()>0.5:
		flip_legs = True
	for ln in mario:
		Y += 1
		if crouching == True and Y in set([12,13]):
			continue
		if flip_legs == True and Y in set([10,11,12,13,14,15]):
			ln = ln.reverse()
		y += 4
		x = ox
		for c in ln:
			x += 4
			if c == ' ':
				continue
			elif c == 'X':
				if blink:
					sdl.draw( vec4(x, y, 4, 4), MarioPal[ '-' ] )
				else:
					sdl.draw( vec4(x, y, 4, 4), MarioPal[ '0' ] )
			else:
				sdl.draw( vec4(x, y, 4, 4), MarioPal[ c ] )


wo = world()
wo.setGravity( vec3(0,-9.81*4,0) )
sp = space()
floor = geomPlane(sp, vec3(0,1,0), -200)
leftwall = geomPlane(sp, vec3(1,0,0), 0)
rightwall = geomPlane(sp, vec3(-1,0,0), -720)
B = body( wo )
m = mass()
m.setSphere( 0.25, 1.0 )
B.setMass( m )
geo = geomBox(sp, vec3(64,64,64) )
geo.setBody(B)

state = {'X':0, 'mx':0, 'my':0, 'jumping':0, 'direction':1, 'crouch':False}

def iterate():
	running = False
	state['jumping'] *= 0.7
	if state['jumping'] >= 4:
		state['jumping'] -= 4
		state['mx'] *= 0.98
	else:
		state['mx'] *= 0.6
	for e in sdl.poll():
		if e["type"] == "KEYDOWN":
			print("key:", e["key"])
			if e["key"] == 113 or e["key"]==80:    ## left key
				state['direction'] = -1
				state['mx'] -= 8
				state['X'] -= 8
				if state['mx'] < -16:
					state['mx'] = -16
			elif e["key"] == 114 or e["key"]==79:  ## right key
				state['direction'] = 1
				state['mx'] += 8; state['X'] += 8
				if state['mx'] > 16:
					state['mx'] = 16
			elif e["key"] == 116 or e["key"]==81: ## key down
				state['jumping'] *= 0.5
				state['crouch'] = True
			elif e["key"]==65 or e["key"] == 44:    ## space
				B.addForce( vec3(0,900,0) )
		elif e["type"] == "KEYUP":
			if e["key"] == 111 or e["key"]==82:
				state['crouch'] = False
			elif e["key"] == 65 or e["key"]==44:    ## space
				if state['jumping'] < 1:
					state['jumping'] += 70
					state['jumping'] += 10 * abs(state['mx'])
					state['mx'] *= 3
	#print(state)
	sdl.clear( vec3(130,130,255) )
	sdl.draw( vec4(0, 210, 720, 50), vec3(80,50, 10) )
	sdl.draw( vec4(0, 208, 720, 4), vec3(100,70, 20) )
	state['X'] += state['mx']
	if state['jumping'] < 1:
		if abs( B.getLinearVel()[0] ) >= 50:
			running = True
	B.addForce( vec3(state['mx']*20.0, -state['jumping'] * 5, 0) )	
	sp.spaceCollide()
	wo.step( 0.2 )
	if state['direction'] == 1:
		draw_mario( B.getPosition(), Mario, state['crouch'], running, random.random()>0.9 )
	else:
		draw_mario( B.getPosition(), MarioReversed, state['crouch'], running, random.random()>0.9 )
	sdl.flip()
	sdl.delay(30)  ## this will do nothing in html

def main():
	sdl.initialize()
	sdl.window( vec2(720, 240) )
	while True: iterate()

main()
