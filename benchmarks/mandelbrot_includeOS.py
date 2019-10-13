#!/usr/bin/env python3
# coding: utf-8
# includeOS has no support for printing to the console past some number of characters without a newline, 
# and will cause a crash. So in this version of mandelbrot the size is lowered, and new line printed.

h = 80
Z = 0.0  ## Zr
z = 0.0  ## Zi
T = 0.0  ## Tr
t = 0.0  ## Ti
C = 0.0  ## Cr
c = 0.0  ## Ci
U = 0.0
V = 0.0
K = 1.5
k = 1.0

def mandelbrot():
	global h, Z,z,T,t,C,c, U,V
	y = 0
	while y < 80:
		y += 1
		x = 0
		print('')
		while x < 80:
			x += 1
			Z, z, T, t = 0.0, 0.0, 0.0, 0.0
			U = x*2
			U /= h
			V = y*2
			V /= h
			C = U - K
			c = V - k

			i = 0
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
				print('*', end='')
			else:
				print('·', end='')

mandelbrot()
