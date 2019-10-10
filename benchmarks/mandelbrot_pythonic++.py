with c++:
	@module( mycppmodule )
	def mandelbrot():
		const double h = 150.0
		double Z = 0.0; double z = 0.0; double T = 0.0; double t = 0.0; double C = 0.0
		double c = 0.0; double U = 0.0; double V = 0.0; double K = 1.5; double k = 1.0
		double y = 0
		while y < 150:
			y ++
			double x = 0
			while x < 150:
				x ++
				Z=0.0; z=0.0; T=0.0; t = 0.0
				U = x*2
				U /= h
				V = y*2
				V /= h
				C = U - K
				c = V - k
				double i = 0
				while i < 50:
					i ++
					if T+t <= 4:
						z = Z*z
						z *= 2
						z += c
						Z = T - t
						Z += C
						T = Z * Z
						t = z * z
				if T+t <= 4:
					std::cout << '*'
				else:
					std::cout << '.'
		return None


import mycppmodule
mycppmodule.mandelbrot()

