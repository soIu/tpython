with javascript:
	bump = 0.0
	def bump_canvas(v):
		bump += 5.0 + v
	ascii2color = { 'R':'rgb(255,0,0)', 'H':'rgb(80,50,5)', '-':'rgb(160,150,100)', 'B':'rgb(0,0,255)', 'Y':'rgb(255,255,0)', '0':'rgb(5,5,5)', 'X':'rgb(5,5,5)', '_':'rgb(255,255,255)' }
	ascii2uni = {'R':unescape('\u2588'),'H':unescape('\u25A6'),'-':unescape('\u262F'),'_':unescape('\u2610')}
	def color_ascii( ln ):
		line = document.createElement('span')
		for (var i=0; i<ln.length; i++):
			char = ln[i]
			if char == '-' || char == 'H':
				span = document.createElement('span')
				span.appendChild( document.createTextNode(ascii2uni[char]) )
			else:
				span = document.createElement('i')
				span.appendChild( document.createTextNode(char) )
			span.style.color = ascii2color[ char ]
			line.appendChild( span )
		return line
	output = document.getElementById('output')
	output.style.background='white'
	output.style.color='green'	
	canvas = document.getElementById('canvas')
	canvas.style.position = 'relative'
	canvas.style.zIndex = 100
	canvas.style.top = '75px'
	canvas.style.boxShadow='10px 10px 10px 10px'
	mariodiv = document.createElement('div')
	mariodiv.setAttribute('id', 'MARIO')
	canvas.parentNode.appendChild(mariodiv)
	mariodiv.style.position = 'relative'
	mariodiv.style.zIndex = 99
	mariodiv.style.fontSize = '11px'
	mariodiv.style.lineHeight = '8px'
	Mario = ['_____RRRRR______','____RRRRRRRRR___','____HHH--X-_____','___H-H---X---___','___H-HH---0----_','___HH----00000__','_____--------___','__RRRRBBRRR_____','--RRRRBBBRRRR---','---_RRBYBBBBRR--','--_BBBBBBBBBB___','__BBBBBBBBBBBB__','_BBBBB____BBBB__','HHBBB______BBB__','HHHH_______HHHH_','_HHHHH_____HHHHH' ]
	for (var i=0; i<Mario.length; i++) {mariodiv.appendChild(color_ascii(Mario[i])); mariodiv.appendChild(document.createElement('br'));}
	marioR = document.createElement('div')
	marioR.setAttribute('id', 'MARIOR')
	canvas.parentNode.appendChild(marioR)
	marioR.style.position = 'relative'
	marioR.style.zIndex = 99
	marioR.style.fontSize = '11px'
	marioR.style.lineHeight = '8px'
	R = ["______RRRRR_____","___RRRRRRRRR____","_____-X--HHH____","___---X---H-H___","_----0---HH-H___","__00000----HH___","___--------_____","_____RRRBBRRRR__","---RRRRBBBRRRR--","--RRBBBBYBRR_---","___BBBBBBBBBB_--","__BBBBBBBBBBBB__","__BBBB____BBBBB_","__BBB______BBBHH","_HHHH_______HHHH","HHHHH_____HHHHH_"]
	for (var i=0; i<R.length; i++) {marioR.appendChild(color_ascii(R[i])); marioR.appendChild(document.createElement('br'));}
	def set_ascii_mario(x,y, direction):
		bump *= 0.75
		canvas.style.top = (75 - bump) + 'px'
		if direction == 1:
			marioR.hidden = true
			mariodiv.hidden = false
			mariodiv.style.left = (x + canvas.offsetLeft) + 'px'
			mariodiv.style.top  = y + 'px'
		else:
			mariodiv.hidden = true
			marioR.hidden = false
			marioR.style.left = (x + canvas.offsetLeft) + 'px'
			marioR.style.top  = y + 'px'


import sdl
import random

crouch_skip  = set([12,13])
legs_indices = set([10,11,12,13,14,15])

Mario = [
'_____@@@@@______',
'____@@@@@@@@@___',
'____===--?-_____',
'___=-=---?---___',
'___=-==---%----_',
'___==----%%%%%__',
'_____--------___',
'__@@@@BB@@@_____',
'--@@@@BBB@@@@---',
'---_@@B$BBBB@@--',
'--_BBBBBBBBBB___',
'__BBBBBBBBBBBB__',
'_BBBBB____BBBB__',
'==BBB______BBB__',
'====_______====_',
'_=====_____=====' ]
## note: there is a bug with global list comps and emscripten, (desktop with gcc is OK)
## when MarioReversed is created it bleeds some of the strings into the tpvm registers,
## this invalid data is then passed to the set constructor, which will then crash.
## the workaround is to make the crouch_skip set before making MarioReversed
MarioReversed = [ s.reverse() for s in Mario ]

MarioPal = { '@':vec3(255,0,0), '=':vec3(80,50,5), '-':vec3(160,150,100), 'B':vec3(0,0,255), '$':vec3(255,255,0), '%':vec3(5,5,5) }

Bricks = [
'____________BBBBBBB',
'___________B_______',
'__________BB_______',
'________BBB________',
'_____BBB___________',
'___BB______________',
'_BBB_______________']

BrickBodies = []
HiddenBricks = []

def make_bricks(wo, sp):
	y = -40
	for ln in Bricks:
		x = 100
		y -= 32
		for c in ln:
			x += 32
			if c == '_':
				continue
			else:
				brick = body(wo)
				brick.setPosition( vec3(x,y,0) )
				ma = mass()
				ma.setSphere( 0.25, 1.0 )
				brick.setMass( ma )
				geo = geomBox(sp, vec3(32,32,32) )
				geo.setBody(brick)
				joint = fixedJoint(wo, brick, 0.5)
				BrickBodies.append(brick)

def draw_bricks():
	for brick in BrickBodies:
		pos = brick.getPosition()
		sdl.draw( vec4(pos[0], -float(pos[1]+12), 32, 32), vec3(200,50,0) )
		sdl.draw( vec4(pos[0], -float(pos[1]+14), 32, 8), vec3(220,80,0) )

Cloud = [
'_____--_________',
'____------__--__',
'__--------------',
'--------------__',
'__----------____',
'____----________',]

bgstate = {"cloudx":750.0}

def draw_background():
	sdl.clear( vec3(130,130,255) )
	sdl.draw( vec4(0, 310, 720, 50), vec3(80,50, 10) )
	sdl.draw( vec4(0, 308, 720, 4), vec3(100,70, 20) )
	bgstate["cloudx"] -= 0.25
	x = bgstate["cloudx"]
	if x < -300:
		bgstate["cloudx"] = 800.0
	y = 0
	for ln in Cloud:
		y += 16
		x = bgstate["cloudx"]
		for c in ln:
			x += 16
			if c == '_':
				continue
			else:
				sdl.draw( vec4(x, y, 16, 16), vec3(255,255,255) )


def draw_mario(vec, mario, crouching, running, blink ):
	ox = vec[0] -64
	oy = -float(vec[1]+64)
	y = oy
	Y = 0
	x = 0
	if crouching == True:
		y += 16
	flip_legs = False
	if running==True and random.random()>0.5:
		flip_legs = True
	for ln in mario:
		Y += 1
		if crouching == True and (Y in crouch_skip):
			continue
		if flip_legs == True and (Y in legs_indices):
			pass
		y += 8
		x = ox
		for c in ln:
			x += 8
			if c == '_':
				continue
			elif c == '?':
				if blink:
					sdl.draw( vec4(x, y, 8, 8), MarioPal[ '-' ] )
				else:
					sdl.draw( vec4(x, y, 8, 8), MarioPal[ '%' ] )
			else:
				sdl.draw( vec4(x, y, 8, 8), MarioPal[ c ] )

## note that this callback is called from the ODE AOT/C++ module,
## so arguments are always passed as a list, which you must manually unpack.
@typedef(args=std::vector<tp_obj>)
def on_collision(  args ):
	m = args[0]
	b = args[1]
	mpos = m.getPosition()
	bpos = b.getPosition()
	if mpos[1]+64 < int(bpos[1]):
		bump_canvas( m.getLinearVel()[1]*0.25 )
	else:
		pass

wo = world()
sp = space()
B = body( wo )
state = {'pressed':False, 'mx':0, 'my':0, 'jumping':0, 'direction':1, 'crouch':False, 'roof':None}

def iterate() ->void:
	running = False
	state["jumping"] *= 0.7
	if state["jumping"] >= 4:
		state["jumping"] -= 4
		state["mx"] *= 0.98
	else:
		state["mx"] *= 0.6
	for e in sdl.poll():
		if e["type"] == "KEYDOWN":
			print("key:", e["key"])
			if e["key"] == 113 or e["key"]==80:    ## left key
				state["direction"] = -1
				state["mx"] -= 8
				if state["mx"] < -16:
					state["mx"] = -16
			elif e["key"] == 114 or e["key"]==79:  ## right key
				state["direction"] = 1
				state["mx"] += 8
				if state["mx"] > 16:
					state["mx"] = 16
			elif e["key"] == 116 or e["key"]==81: ## key down
				state["jumping"] *= 0.5
				state["crouch"] = True
			elif e["key"]==65 or e["key"] == 44:    ## space
				B.addForce( vec3(0,1700,0) )
		elif e["type"] == "KEYUP":
			if e["key"] == 111 or e["key"]==82:
				state["crouch"] = False
			elif e["key"] == 65 or e["key"]==44:    ## space
				if state["jumping"] < 1:
					state["jumping"] += 70
					state["jumping"] += 10 * abs( float(state["mx"]) )
					state["mx"] *= 1.5
		elif e["type"] == "PRESS":
			state["pressed"] = True
		elif e["type"] == "CLICK":
			state["pressed"] = False
		elif e["type"] == "MOUSE" and state["pressed"]:
			state["mx"] += e["rx"] * 0.1
			if e["rx"] < 0:
				state["direction"] = -1
			else:
				state["direction"] = 1
			if e["ry"] < 0:
				B.addForce( vec3(0, -float(e["ry"]*5.0), 0) )
	draw_background()
	if state["jumping"] < 1:
		if abs(float( B.getLinearVel()[0] )) >= 50:
			running = True
	B.addForce( vec3(state["mx"]*20.0, -float(state["jumping"]*2.0), 0) )	
	sp.spaceCollide()
	wo.step( 0.2 )
	B.addForce( vec3(0,0, -float( B.getPosition()[2] * 4.5) ) )
	for brick in BrickBodies:
		brick.addForce( vec3(0,0, -float( brick.getPosition()[2] * 2.5)) )
	if state["direction"] == 1:
		draw_mario( B.getPosition(), Mario, state["crouch"], running, random.random()>0.9 )
	else:
		draw_mario( B.getPosition(), MarioReversed, state["crouch"], running, random.random()>0.9 )
	draw_bricks()
	sdl.flip()
	set_ascii_mario( B.getPosition()[0]-60, -float(B.getPosition()[1]+320), state["direction"] )
	sdl.delay(30)  ## this will do nothing in html

def rundemo():
	sdl.initialize()
	sdl.window( vec2(720, 340) )
	floor = geomPlane(sp, vec3(0,1,0), -600)
	leftwall = geomPlane(sp, vec3(1,0,0), -400)
	rightwall = geomPlane(sp, vec3(-1,0,0), -900)
	wo.setGravity( vec3(0,-9.81*6,0) )
	B.setCollisionCallback( on_collision )
	m = mass()
	m.setSphere( 0.25, 1.0 )
	B.setMass( m )
	geo = geomBox(sp, vec3(128,128,128) )
	geo.setBody(B)
	make_bricks( wo, sp )
	while True: iterate()

def main():
	rundemo()

main()
