import sdl

Mario = [
'     RRRRR      ',
'    RRRRRRRRR   ',
'    HHH--0-     ',
'   H-H---0---   ',
'   H-HH---0---- ',
'   HH----00000  ',
'     --------   ',
'  RRRRBBRRR     ',
'--RRRRBBBRRRR---',
'--- RRBYBBBBRR--',
'-- BBBBBBBBBB   ',
'  BBBBBBBBBBBB  ',
' BBBBB    BBBB  ',
'HHBBB      BBB  ',
'HHHH       HHHH ',
' HHHHH     HHHHH',
]
MarioReversed = [ s.reverse() for s in Mario ]

MarioPal = {
	'R': [255,0,0],
	'H': [80,50,5],
	'-': [160,150,100],
	'B': [0,0,255],
	'Y': [255,255,0],
	'0': [5,5,5],
}

def draw_mario(ox, oy, mario, crouching):
	y = oy
	Y = 0
	if crouching == True:
		y += 8
	for ln in mario:
		Y += 1
		if crouching == True and Y in (12,13):
			continue
		y += 4
		x = ox
		for c in ln:
			x += 4
			if c == ' ':
				continue
			sdl.draw( [x, y, 4, 4], MarioPal[ c ] )

def main():
	sdl.initialize()
	s = sdl.window( (720, 240) )
	i = 0
	X = 0
	mx = 0
	my = 0
	jumping = 0
	direction = 1
	crouch = False
	while True:
		i += 1
		jumping *= 0.7
		if jumping >= 4:
			jumping -= 4
			mx *= 0.8
		else:
			mx *= 0.6

		sdl.clear( [130,130,255] )
		sdl.draw( [0, 210, 720, 50], [80,50, 10] )
		sdl.draw( [0, 208, 720, 4], [100,70, 20] )
		for e in sdl.poll():
			if e['type'] == "KEYDOWN":
				print('key:', e['key'])
				if e['key'] == 80:    ## left key
					direction = -1
					mx -= 8; X -= 8
					if mx < -16:
						mx = -16
				elif e['key'] == 79:  ## right key
					direction = 1
					mx += 8; X += 8
					if mx > 16:
						mx = 16
				elif e['key'] == 81: ## key down
					jumping *= 0.5
					crouch = True
			elif e['type'] == "KEYUP":
				if e['key'] == 82:      ## key up
					crouch = False
				elif e['key'] == 44:    ## space
					if jumping < 1:
						jumping += 70
						jumping += 10 * abs(mx)
						mx *= 4
				elif e['key'] in (20,41):  ## q, esc
					return

		X += mx
		if direction == 1:
			draw_mario(X, (my-jumping)+140, Mario, crouch )
		else:
			draw_mario(X, (my-jumping)+140, MarioReversed, crouch )

		sdl.flip()
		sdl.delay(60)

main()
