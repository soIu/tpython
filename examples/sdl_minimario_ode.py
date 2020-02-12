import sdl
import random

crouch_skip  = set([12,13])
legs_indices = set([10,11,12,13,14,15])

Mario = ['_____RRRRR______','____RRRRRRRRR___','____HHH--X-_____','___H-H---X---___','___H-HH---0----_','___HH----00000__','_____--------___','__RRRRBBRRR_____','--RRRRBBBRRRR---','---_RRBYBBBBRR--','--_BBBBBBBBBB___','__BBBBBBBBBBBB__','_BBBBB____BBBB__','HHBBB______BBB__','HHHH_______HHHH_','_HHHHH_____HHHHH' ]
## note: there is a bug with global list comps and emscripten, (desktop with gcc is OK)
## when MarioReversed is created it bleeds some of the strings into the tpvm registers,
## this invalid data is then passed to the set constructor, which will then crash.
## the workaround is to make the crouch_skip set before making MarioReversed
MarioReversed = [ s.reverse() for s in Mario ]

MarioPal = { 'R':vec3(255,0,0), 'H':vec3(80,50,5), '-':vec3(160,150,100), 'B':vec3(0,0,255), 'Y':vec3(255,255,0), '0':vec3(5,5,5) }

Bricks = ['____________BBBBB__','__BB_______B_______','__________BB_______','________BBB________','_____BB____________']

BrickBodies = []

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
				joint = fixedJoint(wo, brick, 0.05)
				BrickBodies.append(brick)

def draw_bricks():
	for brick in BrickBodies:
		pos = brick.getPosition()
		sdl.draw( vec4(pos[0], -float(pos[1]+12), 32, 32), vec3(200,50,0) )
		sdl.draw( vec4(pos[0], -float(pos[1]+14), 32, 8), vec3(220,80,0) )

def draw_background():
	sdl.clear( vec3(130,130,255) )
	sdl.draw( vec4(0, 310, 720, 50), vec3(80,50, 10) )
	sdl.draw( vec4(0, 308, 720, 4), vec3(100,70, 20) )


def draw_mario(vec, mario, crouching, running, blink ):
	ox = vec[0] -32
	oy = -float(vec[1]+32)
	y = oy
	Y = 0
	x = 0
	if crouching == True:
		y += 8
	flip_legs = False
	if running==True and random.random()>0.5:
		flip_legs = True
	for ln in mario:
		Y += 1
		if crouching == True and (Y in crouch_skip):
			continue
		if flip_legs == True and (Y in legs_indices):
			pass
		y += 4
		x = ox
		for c in ln:
			x += 4
			if c == '_':
				continue
			elif c == 'X':
				if blink:
					sdl.draw( vec4(x, y, 4, 4), MarioPal[ '-' ] )
				else:
					sdl.draw( vec4(x, y, 4, 4), MarioPal[ '0' ] )
			else:
				sdl.draw( vec4(x, y, 4, 4), MarioPal[ c ] )

## note that this callback is called from the ODE AOT/C++ module,
## so arguments are always passed as a list, which you must manually unpack.
@typedef(args=std::vector<tp_obj>)
def on_collision(  args ):
	m = args[0]
	b = args[1]
	mpos = m.getPosition()
	bpos = b.getPosition()
	if mpos[1]+32 < int(bpos[1]):
		joint = b.getJoint()
		joint.breakJoint()
	else:
		pass

wo = world()
sp = space()
B = body( wo )
state = {'pressed':False, 'mx':0, 'my':0, 'jumping':0, 'direction':1, 'crouch':False}

def iterate():
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
				B.addForce( vec3(0,900,0) )
		elif e["type"] == "KEYUP":
			if e["key"] == 111 or e["key"]==82:
				state["crouch"] = False
			elif e["key"] == 65 or e["key"]==44:    ## space
				if state["jumping"] < 1:
					state["jumping"] += 70
					state["jumping"] += 10 * abs( float(state["mx"]) )
					state["mx"] *= 3
		elif e["type"] == "PRESS":
			state["pressed"] = True
		elif e["type"] == "CLICK":
			state["pressed"] = False
		elif e["type"] == "MOUSE" and state["pressed"]:
			state["mx"] += e["rx"] * 0.1
			if e["ry"] < 0:
				B.addForce( vec3(0, -float(e["ry"]*5.0), 0) )
	draw_background()
	if state["jumping"] < 1:
		if abs(float( B.getLinearVel()[0] )) >= 50:
			running = True
	B.addForce( vec3(state["mx"]*20.0, -float(state["jumping"]*5.0), 0) )	
	sp.spaceCollide()
	wo.step( 0.2 )
	B.addForce( vec3(0,0, -float( B.getPosition()[2] * 2.5) ) )
	for brick in BrickBodies:
		brick.addForce( vec3(0,0, -float( brick.getPosition()[2] * 2.5)) )
	if state["direction"] == 1:
		draw_mario( B.getPosition(), Mario, state["crouch"], running, random.random()>0.9 )
	else:
		draw_mario( B.getPosition(), MarioReversed, state["crouch"], running, random.random()>0.9 )
	draw_bricks()
	sdl.flip()
	sdl.delay(30)  ## this will do nothing in html

def rundemo():
	sdl.initialize()
	sdl.window( vec2(720, 340) )
	floor = geomPlane(sp, vec3(0,1,0), -300)
	leftwall = geomPlane(sp, vec3(1,0,0), 0)
	rightwall = geomPlane(sp, vec3(-1,0,0), -720)
	wo.setGravity( vec3(0,-9.81*4,0) )
	B.setCollisionCallback( on_collision )
	m = mass()
	m.setSphere( 0.25, 1.0 )
	B.setMass( m )
	geo = geomBox(sp, vec3(64,64,64) )
	geo.setBody(B)
	make_bricks( wo, sp )
	while True: iterate()

def main():
	rundemo()

main()
