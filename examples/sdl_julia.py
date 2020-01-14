import sdl

SW = 320
SH = 240
pal = [((min(255,v)),(min(255,v*3/2)),(min(255,v*2))) for v in range(0,256)]

def julia(s,ca,cb):
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
			sdl.draw([x,y], color )
			#sdl.draw([x,y, 1,1], [255,0,0] )
			sdl.flip()
	for e in sdl.poll():
		if e.type == "KEYUP":
			return True
		elif e.type == "MOUSE":
			print('mouse x:', e.x)
			print('mouse y:', e.y)
	return False

def main():
	print(pal)
	sdl.initialize()
	sdl.window( (SW,SH) )
	i = 0
	while True:
		print(i)
		i += 1
		sdl.clear( [0,0,0] )
		x = i
		y = i+1
		ca=((float(x)/SW) * 2.0 - 1.0)
		cb=((float(y)/SH) * 2.0 - 1.0)
		if julia(s,ca,cb) == True:
			break
		sdl.delay(100)

	
if __name__ == '__main__':
	main()
