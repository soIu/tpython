import sdl				┃MarioReversed = [ s.reverse() for s in Mario ]
import random			┃MarioPal = { 'R':vec3(255,0,0), 'H':vec3(80,50,5), '-':vec3(160,150,100), 'B': vec3(0,0,255),'Y': vec3(255,255,0),'0': vec3(5,5,5) }
Mario = [				┃
'     RRRRR      ',		┃def draw_mario(vec, mario, crouching, running, blink ):
'    RRRRRRRRR   ',		┃	ox = vec.x; oy = -(vec.y+32); y = oy; Y = 0
'    HHH--X-     ',		┃	if crouching == True: y += 8
'   H-H---X---   ',		┃	flip_legs = False
'   H-HH---0---- ',		┃	if running==True and random.random() > 0.5: flip_legs = True
'   HH----00000  ',		┃	for ln in mario:
'     --------   ',		┃		Y += 1
'  RRRRBBRRR     ',		┃		if crouching == True and Y in (12,13): continue
'--RRRRBBBRRRR---',		┃		if flip_legs == True and Y in (10,11,12,13,14,15): ln = ln.reverse()
'--- RRBYBBBBRR--',		┃		y += 4; x = ox
'-- BBBBBBBBBB   ',		┃		for c in ln:
'  BBBBBBBBBBBB  ',		┃			x += 4
' BBBBB    BBBB  ',		┃			if c == ' ': continue
'HHBBB      BBB  ',		┃			elif c == 'X':
'HHHH       HHHH ',		┃				if blink: sdl.draw( vec4(x, y, 4, 4), MarioPal[ '-' ] )
' HHHHH     HHHHH',		┃				else: sdl.draw( vec4(x, y, 4, 4), MarioPal[ '0' ] )
]						┃			else: sdl.draw( vec4(x, y, 4, 4), MarioPal[ c ] )

def main():
	wo = world(); wo.setGravity( vec3(0,-9.81*4,0) );  sp = space()
	floor = geomPlane(sp, vec3(0,1,0), -200); leftwall = geomPlane(sp, vec3(1,0,0), 0); rightwall = geomPlane(sp, vec3(-1,0,0), -720)
	B = body( wo );   m = mass(); m.setSphere( 0.25, 1.0 );  B.setMass( m );  geo = geomBox(sp, vec3(64,64,64) );  geo.setBody(B)
	sdl.initialize(); sdl.window( vec2(720, 240) ); mx = 0;  my = 0;          jumping = 0;   direction = 1;        crouch = False
	while True:
		running = False; jumping *= 0.7
		if jumping >= 4:
			jumping -= 4; mx *= 0.8
		else:
			mx *= 0.6
		sdl.clear( vec3(130,130,255) )
		sdl.draw( vec4(0, 210, 720, 50), vec3(80,50, 10) )
		sdl.draw( vec4(0, 208, 720, 4), vec3(100,70, 20) )
		for e in sdl.poll():
			if e.type == "KEYDOWN":
				print('key:', e.key)
				if e.key == 80:    ## left key
					direction = -1; mx -= 8
					if mx < -16: mx = -16
				elif e.key == 79:  ## right key
					direction = 1; mx += 8
					if mx > 16: mx = 16
				elif e.key == 81: ## key down
					jumping *= 0.5; crouch = True
				elif e.key == 44:    ## space
					B.addForce( vec3(0,80,0) )
			elif e.type == "KEYUP":
				if e.key == 82: crouch = False
				elif e.key == 44:    ## space
					if jumping < 1:
						jumping += 70; jumping += 10 * abs(mx); mx *= 4
				elif e.key in (20,41):  return
		if jumping < 1:
			if abs(B.getLinearVel()[0]) >= 50: running = True
		B.addForce( vec3(mx*5, -jumping*0.5, 0) )	
		sp.spaceCollide(); wo.step(0.2)
		if direction == 1:
			draw_mario(B.getPosition(), Mario, crouch, running, random.random() > 0.9 )
		else:
			draw_mario(B.getPosition(), MarioReversed, crouch, running, random.random() > 0.9 )
		sdl.flip(); sdl.delay(60)
main()
