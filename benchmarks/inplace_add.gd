tool
extends SceneTree
var a = 1
var b = 2
var c = 0
func _init():
	var time_start = OS.get_ticks_msec()
	print('begin test')

	for i in range(1000000):
		c += a + b

	print(c)
	print('ok')
	var elapsed_time = OS.get_ticks_msec() - time_start
	print(elapsed_time/1000.0)
	quit()
	
# to run from the command line: godot -s inplace_add.gd
