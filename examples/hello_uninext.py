import uninext
game = None
def loop():
	print('game.clear')
	game.clear()
	print('game.inputs')
	game.input()
	print('game.update')
	game.update()
	print('game.draw')
	game.draw()
	print('game.show')
	game.show()

def main():
	global game
	print('hello uninext engine')
	game = uninext.Engine()
	#game.mainloop()
	while True: loop()

main()