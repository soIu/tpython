import sdl				┃MarioReversed = [ s.reverse() for s in Mario ]
import random			┃MarioPal = { 'R':[255,0,0], 'H':[80,50,5], '-':[160,150,100], 'B': [0,0,255],'Y': [255,255,0],'0': [5,5,5] }
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
'HHBBB      BBB  ',		┃			sdl.draw( [x, y, 4, 4], MarioPal[ c ] )
'HHHH       HHHH ',		┃
' HHHHH     HHHHH',		┃
]						┃

def main():
	sdl.initialize(); sdl.window( (720, 240) )
	i = 0; X = 0; mx = 0; my = 0; jumping = 0
	direction = 1; crouch = False
	while True:
		i += 1; running = False; jumping *= 0.7
		if jumping >= 4:
			jumping -= 4; mx *= 0.8
		else:
			mx *= 0.6
		sdl.clear( [130,130,255] )
		sdl.draw( [0, 210, 720, 50], [80,50, 10] )
		sdl.draw( [0, 208, 720, 4], [100,70, 20] )
		for e in sdl.poll():
			if e.type == "KEYDOWN":
				print('key:', e.key)
				if e.key == 80:    ## left key
					direction = -1; mx -= 8; X -= 8
					if mx < -16: mx = -16
				elif e.key == 79:  ## right key
					direction = 1; mx += 8; X += 8
					if mx > 16: mx = 16
				elif e.key == 81: ## key down
					jumping *= 0.5; crouch = True
			elif e.type == "KEYUP":
				if e.key == 82: crouch = False
				elif e.key == 44:    ## space
					if jumping < 1:
						jumping += 70; jumping += 10 * abs(mx); mx *= 4
				elif e.key in (20,41):  return
		X += mx
		if jumping < 1:
			if abs(mx) >= 2: running = True
		if direction == 1:
			draw_mario(X, (my-jumping)+140, Mario, crouch, running )
		else:
			draw_mario(X, (my-jumping)+140, MarioReversed, crouch, running )
		sdl.flip(); sdl.delay(60)
main()
