with c++:
	class Foo(Object3D):
		int speed
		def on_update(self):
			x = self.rx()
			x += self.speed
			if x >= 360:
				x = 0
			self.rx( x )
		def __init__(self, double x, double y, double z, double rx, double ry, double rz ):
			self.x(x)
			self.y(y)
			self.z(z)
			self.rx(rx)
			self.ry(ry)
			self.rz(rz)
			self.speed = 1
## end of py++


