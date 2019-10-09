tool
extends SceneTree

var h = 150.0
var Z = 0.0  ## Zr
var z = 0.0  ## Zi
var T = 0.0  ## Tr
var t = 0.0  ## Ti
var C = 0.0  ## Cr
var c = 0.0  ## Ci
var U = 0.0
var V = 0.0
var K = 1.5
var k = 1.0

func _init():
	var time_start = OS.get_ticks_msec()

	var y = 0
	while y < 150:
		y += 1
		var x = 0
		while x < 150:
			x += 1
			Z=0.0
			z=0.0
			T=0.0
			t=0.0

			U = x*2
			U /= h
			V = y*2
			V /= h
			C = U - K
			c = V - k

			var i = 0
			while i < 50:
				i += 1
				if T+t <= 4:
					z = Z*z
					z *= 2
					z += c
					Z = T - t
					Z += C
					T = Z * Z
					t = z * z

			if T+t <= 4:
				printraw('*')
			else:
				printraw('·')


	var elapsed_time = OS.get_ticks_msec() - time_start
	print(elapsed_time/1000.0)
	quit()
