#include <SDL2/SDL.h>

static SDL_Window *_sdl_window = NULL;
//SDL_Renderer *_sdl_renderer = NULL;  // SDL_Renderer can not be used with SDL_GetWindowSurface
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
	tp_obj clr = TP_TYPE(TP_LIST);
	int r = tp_get(tp,clr,tp_number(0)).number.val;
	int g = tp_get(tp,clr,tp_number(1)).number.val;
	int b = tp_get(tp,clr,tp_number(2)).number.val;
	//SDL_SetRenderDrawColor(_sdl_renderer, r, g, b, 255);
	//SDL_RenderClear(_sdl_renderer);
	SDL_Rect rect;
	rect.x = 0;
	rect.y = 0;
	rect.w = _sdl_width;
	rect.h = _sdl_height;
	Uint32 c = SDL_MapRGB(_sdl_window_surf->format,r,g,b);
	SDL_FillRect(_sdl_window_surf, &rect, c);
	return tp_None;
}

tp_obj _sdl_display_flip(TP) {
	//SDL_RenderPresent(_sdl_renderer);
	SDL_UpdateWindowSurface(_sdl_window);
	return tp_None;
}
tp_obj _sdl_delay(TP) {
	tp_obj ms = TP_TYPE(TP_NUMBER);
	SDL_Delay((int)ms.number.val );
	return tp_None;
}

Uint32 _sdl_list_to_color(TP,tp_obj clr,SDL_Surface *s) {
	int r,g,b;
	r = tp_get(tp,clr,tp_number(0)).number.val;
	g = tp_get(tp,clr,tp_number(1)).number.val;
	b = tp_get(tp,clr,tp_number(2)).number.val;
	return SDL_MapRGB(s->format,r,g,b);
}


tp_obj _sdl_create_window(TP) {
	tp_obj sz = TP_TYPE(TP_LIST);
	int w = tp_get(tp,sz,tp_number(0)).number.val;
	int h = tp_get(tp,sz,tp_number(1)).number.val;
	_sdl_width = w;
	_sdl_height = h;
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
	if (!_sdl_window_surf)
		throw "SDL ERROR: could not get sdl surface from window";

	return tp_None;
}

tp_obj _sdl_draw(TP) {
	tp_obj pos = TP_TYPE(TP_LIST);
	tp_obj clr = TP_TYPE(TP_LIST);
	SDL_Rect r;
	r.x = tp_get(tp,pos,tp_number(0)).number.val;
	r.y = tp_get(tp,pos,tp_number(1)).number.val;
	if (tp_len(tp,pos).number.val == 4) {
		r.w = tp_get(tp,pos,tp_number(2)).number.val;
		r.h = tp_get(tp,pos,tp_number(3)).number.val;
	} else {
		r.w = 1;
		r.h = 1;
	}
	Uint32 c = _sdl_list_to_color(tp, clr, _sdl_window_surf);
	SDL_FillRect(_sdl_window_surf, &r, c);
	return tp_None;
}


tp_obj _sdl_event_get(TP) {
	SDL_Event e;
	tp_obj r = tp_list(tp);
	while (SDL_PollEvent(&e)) {
		tp_obj d = tp_object(tp);
		tp_set(tp,d,tp_string_atom(tp, "type"),tp_number(e.type));
		switch (e.type) {
			case SDL_KEYDOWN:
				tp_set(tp,d,tp_string_atom(tp, "type"),tp_string_atom(tp,"KEYDOWN"));
				tp_set(tp,d,tp_string_atom(tp, "key"),tp_number(e.key.keysym.scancode));
				tp_set(tp,d,tp_string_atom(tp, "sym"),tp_number(e.key.keysym.sym));
				tp_set(tp,d,tp_string_atom(tp, "mod"),tp_number(e.key.keysym.mod));
				break;
			case SDL_KEYUP:
				tp_set(tp,d,tp_string_atom(tp, "type"),tp_string_atom(tp,"KEYUP"));
				tp_set(tp,d,tp_string_atom(tp, "key"),tp_number(e.key.keysym.scancode));
				tp_set(tp,d,tp_string_atom(tp, "sym"),tp_number(e.key.keysym.sym));
				tp_set(tp,d,tp_string_atom(tp, "mod"),tp_number(e.key.keysym.mod));
				break;
			case SDL_MOUSEMOTION:
				tp_set(tp,d,tp_string_atom(tp, "type"),tp_string_atom(tp,"MOUSE"));
				tp_set(tp,d,tp_string_atom(tp, "x"),tp_number(e.motion.x));
				tp_set(tp,d,tp_string_atom(tp, "y"),tp_number(e.motion.y));
				tp_set(tp,d,tp_string_atom(tp, "rx"),tp_number(e.motion.xrel));
				tp_set(tp,d,tp_string_atom(tp, "ry"),tp_number(e.motion.yrel));
				tp_set(tp,d,tp_string_atom(tp, "state"),tp_number(e.motion.state));
				break;
			case SDL_MOUSEBUTTONDOWN:
			case SDL_MOUSEBUTTONUP:
				tp_set(tp,d,tp_string_atom(tp, "type"),tp_string_atom(tp,"CLICK"));
				tp_set(tp,d,tp_string_atom(tp, "x"),tp_number(e.button.x));
				tp_set(tp,d,tp_string_atom(tp, "y"),tp_number(e.button.y));
				tp_set(tp,d,tp_string_atom(tp, "button"),tp_number(e.button.button));
				break;
		}
		//tp_set(tp,r,tp_None,d);
		tpd_list_append(tp, r.list.val, d);
	}
	return r;
}

void tp_module_sdl_init(TP) {
	tp_obj g = tp_import(tp, tp_string_atom(tp, "sdl"), tp_None, tp_string_atom(tp, "<builtin>"));
	tp_set(tp,g,tp_string_atom(tp, "initialize"),tp_function(tp,_sdl_init_video));
	tp_set(tp,g,tp_string_atom(tp, "window"),tp_function(tp,_sdl_create_window));
	tp_set(tp,g,tp_string_atom(tp, "clear"),tp_function(tp,_sdl_display_clear));
	tp_set(tp,g,tp_string_atom(tp, "flip"),tp_function(tp,_sdl_display_flip));
	tp_set(tp,g,tp_string_atom(tp, "draw"),tp_function(tp,_sdl_draw));
	tp_set(tp,g,tp_string_atom(tp, "delay"),tp_function(tp,_sdl_delay));
	tp_set(tp,g,tp_string_atom(tp, "quit"),tp_function(tp,_sdl_quit));
	tp_set(tp,g,tp_string_atom(tp, "poll"),tp_function(tp,_sdl_event_get));
}