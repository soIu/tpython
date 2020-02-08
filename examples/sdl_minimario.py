import sdl				┃MarioReversed = [ s.reverse() for s in Mario ]
import random			┃MarioPal = { 'R':vec3(255,0,0), 'H':vec3(80,50,5), '-':vec3(160,150,100), 'B': vec3(0,0,255),'Y': vec3(255,255,0),'0': vec3(5,5,5) }
Mario = [				┃
'     RRRRR      ',		┃def draw_mario(ox, oy, mario, crouching, running ):
'    RRRRRRRRR   ',		┃	y = oy; Y = 0
'    HHH--0-     ',		┃	if crouching == True: y += 8
'   H-H---0---   ',		┃	flip_legs = False
'   H-HH---0---- ',		┃	if running==True and random.random() > 0.5: flip_legs = True
'   HH----00000  ',		┃	for ln in mario:
'     --------   ',		┃		Y += 1
'  RRRRBBRRR     ',		┃		if crouching == True and Y in (12,13): continue
'--RRRRBBBRRRR---',		┃		if flip_legs == True and Y in (10,11,12,13,14,15): ln = ln.reverse()
'--- RRBYBBBBRR--',		┃		y += 4; x = ox
'-- BBBBBBBBBB   ',		┃		for c in ln:
'  BBBBBBBBBBBB  ',		┃			x += 4
' BBBBB    BBBB  ',		┃			if c == ' ': continue
'HHBBB      BBB  ',		┃			sdl.draw( vec4(x, y, 4, 4), MarioPal[ c ] )
'HHHH       HHHH ',		┃
' HHHHH     HHHHH',		┃
]						┃

state = {'X':0, 'mx':0, 'my':0, 'jumping':0, 'direction':1, 'crouch':False}

def iterate():
	running = False
	state['jumping'] *= 0.7
	if state['jumping'] >= 4:
		state['jumping'] -= 4; state['mx'] *= 0.98
	else:
		state['mx'] *= 0.6
	for e in sdl.poll():
		if e.type == "KEYDOWN":
			print('key:', e.key)
			if e.key == 113 or e.key==80:    ## left key
				state['direction'] = -1
				state['mx'] -= 8; state['X'] -= 8
				if state['mx'] < -16: state['mx'] = -16
			elif e.key == 114 or e.key==79:  ## right key
				state['direction'] = 1
				state['mx'] += 8; state['X'] += 8
				if state['mx'] > 16: state['mx'] = 16
			elif e.key == 116 or e.key==81: ## key down
				state['jumping'] *= 0.5; state['crouch'] = True
		elif e.type == "KEYUP":
			if e.key == 111 or e.key==82: state['crouch'] = False
			elif e.key == 65 or e.key==44:    ## space
				if state['jumping'] < 1:
					state['jumping'] += 70
					state['jumping'] += 10 * abs(state['mx'])
					state['mx'] *= 4
	sdl.clear( vec3(130,130,255) )
	sdl.draw( vec4(0, 210, 720, 50), vec3(80,50, 10) )
	sdl.draw( vec4(0, 208, 720, 4), vec3(100,70, 20) )
	state['X'] += state['mx']
	if state['jumping'] < 1:
		if abs(state['mx']) >= 2: running = True
	if state['direction'] == 1:
		draw_mario(state['X'], (state['my']-state['jumping'])+140, Mario, state['crouch'], running )
	else:
		draw_mario(state['X'], (state['my']-state['jumping'])+140, MarioReversed, state['crouch'], running )
	sdl.flip()
	sdl.delay(30)  ## this will do nothing in html

def main():
	sdl.initialize(); sdl.window( vec2(720, 240) )
	## calling a function from a `while True: myfunc()` will be translated to a emscripten main loop function
	while True: iterate()

main()
