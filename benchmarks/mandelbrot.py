#!/usr/bin/env python3
# coding: utf-8

w = 150.0
h = 150.0
y = 0.0
Z = 0.0  ## Zr
z = 0.0  ## Zi
T = 0.0  ## Tr
t = 0.0  ## Ti
C = 0.0  ## Cr
c = 0.0  ## Ci


def mandelbrot():
	global w,h,y, Z,z,T,t,C,c
	while y < h:
		x = 0.0
		while x < w:
			Z, z, T, t = 0.0, 0.0, 0.0, 0.0
			C = 2*x/w - 1.5
			c = 2*y/h - 1.0

			i = 0
			while i < 50 and T+t <= 4:
				z = 2*Z*z + c
				Z = T - t + C
				T = Z * Z
				t = z * z
				i += 1

			if T+t <= 4:
				print('*', end='')
				pass
			else:
				print('·', end='')
				pass

			x = x+1

		y = y+1

mandelbrot()
