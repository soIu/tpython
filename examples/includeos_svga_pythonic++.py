## this demo is compiled with: `./rebuild.py --includeos --svga includeos_svga_pythonic++.py`
# Copyright 2015 Oslo and Akershus University College of Applied Sciences and Alfred Bratterud Licensed under the Apache License
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

with c++:
	import <timers>
	import <array>
	import <cmath>
	import <deque>
	import <x86intrin.h>
	using namespace std::chrono
	static uint8_t backbuffer[320*200] __attribute__((aligned(16)))
	def set_pixel(int x, int y, uint8_t cl):
		if x >= 0 && x < 320 && y >= 0 && y < 200:
			backbuffer[y * 320 + x] = cl
	def clear():
		memset(backbuffer, 0, sizeof(backbuffer))
	static int timev = 0
	class Star:
		float x, y
		uint8_t cl
		Star() {
		  x = rand() % 320
		  y = rand() % 200
		  cl = 18 + rand() % 14
		}
		def render():
			uint8_t dark = std::max(cl - 6, 16)
			set_pixel(x+1, y, dark)
			set_pixel(x-1, y, dark)
			set_pixel(x, y+1, dark)
			set_pixel(x, y-1, dark)
			set_pixel(x, y, cl)
		def modulate():
			clear()
			if cl == 16:
				return
			float dx = (x - 160)
			float dy = (y - 100)
			if dx == 0 && dy == 0:
				return
			float mag = 1.0f / sqrtf(dx*dx + dy*dy)
			dx *= mag
			dy *= mag
			x += dx * 1.0f
			y += dy * 1.0f
			render();
		def clear():
			set_pixel(x+1, y, 0)
			set_pixel(x-1, y, 0)
			set_pixel(x, y+1, 0)
			set_pixel(x, y-1, 0)
			set_pixel(x, y, 0)
	static std::deque<Star> stars
	@module( mymodule )
	def start():
		VGA_gfx::set_mode(VGA_gfx::MODE_320_200_256)
		VGA_gfx::clear()
		VGA_gfx::apply_default_palette()
		clear()
		auto update_callback = def[](int):
			## add new (random) star
			if rand() % 2 == 0:
				Star star
				star.render()
				stars.push_back(star)
			## render screen
			VGA_gfx::blit_from(backbuffer)
			## work on backbuffer
			for (auto& star : stars) { star.modulate(); }
			if stars.size() > 50:
				auto& dead_star = stars.front()
				dead_star.clear()
				stars.pop_front()
			timev++
		Timers::periodic(16ms, update_callback)

import mymodule
mymodule.start()
