import sdl

SW = 320
SH = 240
pal = [ vec3(min(255,v), min(255,v*3/2), min(255,v*2)) for v in range(256)]

def julia(s,ca,cb):
	print('julia....')
	for y in range(SH):
		for x in range(SW):
			i = 0
			a = x / SW
			a *= 4.0 - 2.0
			b=((float(y)/SH) * 4.0 - 2.0)
			while i < 15 and (a*a)+(b*b)<4.0:
				na=(a*a)-(b*b)+ca
				nb=(2.0*a*b)+cb
				a=na
				b=nb
				i = i +1
			color = pal[ i*16 ]
			sdl.draw( vec2(x,y), color )
			sdl.flip()
	for e in sdl.poll():
		if e.type == "KEYUP":
			return True
		elif e.type == "MOUSE":
			print('mouse x:', e.x)
			print('mouse y:', e.y)
	return False

I = [1]
def iterate():
	print(I)
	I[0] += 1
	sdl.clear( vec3(0,0,0) )
	x = I[0]
	y = I[0]+1
	ca=((float(x)/SW) * 2.0 - 1.0)
	cb=((float(y)/SH) * 2.0 - 1.0)
	julia(s,ca,cb)
	sdl.flip()
	sdl.delay(100)

def main():
	print('enter main')
	sdl.initialize()
	sdl.window( vec2(SW,SH) )
	while True: iterate()

	
main()
