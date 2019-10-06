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
MarioPal = {
	'R': [255,0,0],
	'H': [80,50,5],
	'-': [160,150,100],
	'B': [0,0,255],
	'Y': [255,255,0],
	'0': [5,5,5],
}

def draw_mario(ox, oy):
	y = oy
	for ln in Mario:
		y += 4
		x = ox
		for c in ln:
			x += 4
			if c == ' ':
				continue
			sdl.draw( [x, y, 4, 4], MarioPal[ c ] )

def main():
	sdl.initialize()
	s = sdl.window( (320, 240) )
	i = 0
	mx = 0
	my = 0
	jumping = 0
	while True:
		i += 1
		jumping *= 0.7
		if jumping >= 4:
			jumping -= 4
		sdl.clear( [0,0,0] )
		for e in sdl.poll():
			if e['type'] == "KEYDOWN":
				print('key:', e['key'])
				if e['key'] == 80:    ## left key
					mx -= 8
				elif e['key'] == 79:  ## right key
					mx += 8
				elif e['type'] == 81: ## key down
					jumping *= 0.5
					crouch = True
			elif e['type'] == "KEYUP":
				if e['key'] == 82:   ## key up
					jumping += 80

		draw_mario(mx, (my-jumping)+140 )
		sdl.flip()
		sdl.delay(60)

main()
