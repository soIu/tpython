// note: SDL1 works better with Emscripten, so SDL2 is deprecated

#ifdef USE_SDL2_DEPRECATED
	#include <SDL2/SDL.h>
	static SDL_Window *_sdl_window = NULL;
	//SDL_Renderer *_sdl_renderer = NULL;  // SDL_Renderer can not be used with SDL_GetWindowSurface
#else
	#include <SDL/SDL.h>
#endif

static SDL_Surface *_sdl_window_surf = NULL;
static int _sdl_width = 0;
static int _sdl_height = 0;

tp_obj _sdl_init_video(TP) {
	if (SDL_Init(SDL_INIT_VIDEO) < 0)
		std::cout << "WARN: could not init sdl video" << std::endl;
	return tp_None;
}

tp_obj _sdl_quit(TP) {
	SDL_Quit();
	return tp_None;
}

tp_obj _sdl_display_clear(TP) {
	//print("sdl.clearing...");
	tp_obj clr = TP_OBJ();
	int r = clr[0].number.val;
	int g = clr[1].number.val;
	int b = clr[2].number.val;
	//SDL_SetRenderDrawColor(_sdl_renderer, r, g, b, 255);
	//SDL_RenderClear(_sdl_renderer);
	SDL_Rect rect;
	rect.x = 0;
	rect.y = 0;
	rect.w = _sdl_width;
	rect.h = _sdl_height;
	//auto surf = SDL_GetVideoSurface();
	//SDL_LockSurface(_sdl_window_surf);

	Uint32 c = SDL_MapRGB(_sdl_window_surf->format,r,g,b);
	SDL_FillRect(_sdl_window_surf, &rect, c);
	//Uint32 c = SDL_MapRGB(surf->format,r,g,b);
	//SDL_FillRect(surf, &rect, c);

	//SDL_UnlockSurface(_sdl_window_surf);

	return tp_None;
}

tp_obj _sdl_display_flip(TP) {
	#ifdef USE_SDL2_DEPRECATED
	//SDL_RenderPresent(_sdl_renderer);
	SDL_UpdateWindowSurface(_sdl_window);
	#else
	// https://wiki.libsdl.org/SDL_BlitSurface
	//SDL_BlitSurface( _sdl_window_surf, NULL, SDL_GetVideoSurface(), NULL);
	//SDL_Flip( SDL_GetVideoSurface() );
	//SDL_Flip( _sdl_window_surf );
	SDL_UpdateRect(_sdl_window_surf, 0,0,0,0);
	#endif
	return tp_None;
}
tp_obj _sdl_delay(TP) {
	tp_obj ms = TP_TYPE(TP_NUMBER);
	SDL_Delay((int)ms.number.val );
	return tp_None;
}

Uint32 _sdl_list_to_color(TP,tp_obj clr,SDL_Surface *s) {
	int r,g,b;
	r = clr[0];
	g = clr[1];
	b = clr[2];
	return SDL_MapRGB(s->format,r,g,b);
}


tp_obj _sdl_create_window(TP) {
	print("sdl_create_window....");
	tp_obj sz = TP_OBJ();
	int w = sz[0];
	int h = sz[1];
	_sdl_width = w;
	_sdl_height = h;
	#ifdef USE_SDL2_DEPRECATED
	_sdl_window = SDL_CreateWindow(
		"TPython", 
		SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, 
		w, h, SDL_WINDOW_SHOWN
	);
	if (_sdl_window == NULL)
		throw "SDL ERROR: could not create sdl window";
	//_sdl_renderer = SDL_CreateRenderer(_sdl_window, -1, 0);
	//if (!_sdl_window_surf)
	//	throw "WARN: could not get sdl surface from window";
	_sdl_window_surf = SDL_GetWindowSurface(_sdl_window);
	#else
	_sdl_window_surf = SDL_SetVideoMode( w, h, 32, SDL_SWSURFACE );
	//if (! SDL_SetVideoMode( w, h, 32, SDL_ANYFORMAT ) ) {
	//	print("SDL failed to set the video mode");
	//	throw "SDL failed to set the video mode";
	//}
	//_sdl_window_surf = SDL_CreateRGBSurface(0, w, h, 32, 0, 0, 0, 0);
	#endif

	if (!_sdl_window_surf) {
		print("SDL ERROR: could not get sdl surface from window");
		throw "SDL ERROR: could not get sdl surface from window";
	} else {
		print(_sdl_window_surf);
	}

	return tp_None;
}

tp_obj _sdl_draw(TP) {
	//print("sdl.draw...");
	tp_obj pos = TP_OBJ();
	tp_obj clr = TP_OBJ();
	SDL_Rect r;
	r.x = pos[0].number.val;
	r.y = pos[1].number.val;
	if (pos.type.type_id==TP_VEC2) {
		r.w = 1;
		r.h = 1;
	} else if (pos.type.type_id==TP_QUAT) {
		r.w = pos[2].number.val;
		r.h = pos[3].number.val;	
	} else if (tp_len(tp,pos).number.val == 4) {
		r.w = tp_get(tp,pos,tp_number(2)).number.val;
		r.h = tp_get(tp,pos,tp_number(3)).number.val;
	} else {
		r.w = 1;
		r.h = 1;
	}
	//SDL_LockSurface(_sdl_window_surf);

	Uint32 c = _sdl_list_to_color(tp, clr, _sdl_window_surf);
	SDL_FillRect(_sdl_window_surf, &r, c);

	//SDL_UnlockSurface(_sdl_window_surf);

	return tp_None;
}


tp_obj _sdl_event_get(TP) {
	SDL_Event e;
	tp_obj r = tp_list(tp);
	while (SDL_PollEvent(&e)) {
		tp_obj d = tp_extern_interface(tp);
		tp_set(tp,d, "type", tp_number(e.type));
		switch (e.type) {
			case SDL_KEYDOWN:
				tp_set(tp,d, "type", "KEYDOWN");
				tp_set(tp,d, "key",  tp_number(e.key.keysym.scancode));
				tp_set(tp,d, "sym",  tp_number(e.key.keysym.sym));
				tp_set(tp,d, "mod",  tp_number(e.key.keysym.mod));
				break;
			case SDL_KEYUP:
				tp_set(tp,d, "type", "KEYUP");
				tp_set(tp,d, "key",  tp_number(e.key.keysym.scancode));
				tp_set(tp,d, "sym",  tp_number(e.key.keysym.sym));
				tp_set(tp,d, "mod",  tp_number(e.key.keysym.mod));
				break;
			case SDL_MOUSEMOTION:
				tp_set(tp,d, "type", "MOUSE");
				tp_set(tp,d, "x",  tp_number(e.motion.x));
				tp_set(tp,d, "y",  tp_number(e.motion.y));
				tp_set(tp,d, "rx", tp_number(e.motion.xrel));
				tp_set(tp,d, "ry", tp_number(e.motion.yrel));
				tp_set(tp,d, "state", tp_number(e.motion.state));
				break;
			case SDL_MOUSEBUTTONDOWN:
			case SDL_MOUSEBUTTONUP:
				tp_set(tp,d, "type", "CLICK");
				tp_set(tp,d, "x", tp_number(e.button.x));
				tp_set(tp,d, "y", tp_number(e.button.y));
				tp_set(tp,d, "button", tp_number(e.button.button));
				break;
		}
		//tp_set(tp,r,tp_None,d);
		tpd_list_append(tp, r.list.val, d);
	}
	return r;
}

void tp_module_sdl_init(TP) {
	tp_obj g = tp_import(tp, "sdl", "<builtin>");
	tp_set(tp,g, "initialize", tp_function(tp,_sdl_init_video));
	tp_set(tp,g, "window", tp_function(tp,_sdl_create_window));
	tp_set(tp,g, "clear",  tp_function(tp,_sdl_display_clear));
	tp_set(tp,g, "flip",   tp_function(tp,_sdl_display_flip));
	tp_set(tp,g, "draw",   tp_function(tp,_sdl_draw));
	tp_set(tp,g, "delay",  tp_function(tp,_sdl_delay));
	tp_set(tp,g, "quit",   tp_function(tp,_sdl_quit));
	tp_set(tp,g, "poll",   tp_function(tp,_sdl_event_get));
}
