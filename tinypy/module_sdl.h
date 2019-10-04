#include <SDL2/SDL.h>

#define _SDL_TYPE_SURF 0x1001
SDL_Window *_sdl_window = NULL;
SDL_Renderer *_sdl_renderer = NULL;

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
	SDL_SetRenderDrawColor(_sdl_renderer, r, g, b, 255);
	SDL_RenderClear(_sdl_renderer);
	return tp_None;
}

tp_obj _sdl_display_flip(TP) {
	SDL_RenderPresent(_sdl_renderer);
	return tp_None;
}


Uint32 _sdl_list_to_color(TP,tp_obj clr,SDL_Surface *s) {
	int r,g,b;
	r = tp_get(tp,clr,tp_number(0)).number.val;
	g = tp_get(tp,clr,tp_number(1)).number.val;
	b = tp_get(tp,clr,tp_number(2)).number.val;
	return SDL_MapRGB(s->format,r,g,b);
}

void _sdl_surf_free(TP,tp_obj d) {
	if (d.type.magic != _SDL_TYPE_SURF) throw "not an sdl surface";
	SDL_FreeSurface((SDL_Surface*)d.data.val);
}

SDL_Surface *_sdl_obj_to_surf(TP,tp_obj self) {
	tp_obj d = tp_get(tp,self,tp_string_atom(tp, "__surface__"));
	if (d.type.magic != _SDL_TYPE_SURF) throw "not an sdl surface";
	return (SDL_Surface*)d.data.val;
}

tp_obj _sdl_surface_set_at(TP) {
	tp_obj self = TP_OBJ();
	tp_obj pos = TP_TYPE(TP_LIST);
	tp_obj clr = TP_TYPE(TP_LIST);
	SDL_Rect r;
	r.x = tp_get(tp,pos,tp_number(0)).number.val;
	r.y = tp_get(tp,pos,tp_number(1)).number.val;
	r.w = 1; r.h = 1;
	SDL_Surface *s = _sdl_obj_to_surf(tp,self);
	Uint32 c = _sdl_list_to_color(tp,clr,s);
	SDL_FillRect(s, &r, c);
	return tp_None;
}

tp_obj _sdl_surf_to_obj(TP,SDL_Surface *s) {
	tp_obj self = tp_dict(tp);
	tp_obj d = tp_data(tp,_SDL_TYPE_SURF,s);
	d.data.info->free = _sdl_surf_free;
	tp_set(tp,self,tp_string_atom(tp, "__surface__"),d);
	tp_set(tp,self,tp_string_atom(tp, "set_at"),tp_method(tp,self,_sdl_surface_set_at));
	return self;
}


tp_obj _sdl_create_window(TP) {
	tp_obj sz = TP_TYPE(TP_LIST);
	int w = tp_get(tp,sz,tp_number(0)).number.val;
	int h = tp_get(tp,sz,tp_number(1)).number.val;
	_sdl_window = SDL_CreateWindow(
		"TPython", 
		SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, 
		w, h, SDL_WINDOW_SHOWN
	);
	if (_sdl_window == NULL)
		std::cout << "WARN: could not create sdl window" << std::endl;

	_sdl_renderer = SDL_CreateRenderer(_sdl_window, -1, 0);

	SDL_Surface *s = SDL_GetWindowSurface(_sdl_window);
	if (!s)
		std::cout << "WARN: could not get sdl surface from window" << std::endl;

	return _sdl_surf_to_obj(tp,s);
}

void tp_module_sdl_init(TP) {
	//tp_obj g = tp_dict(tp);
	//tp_set(tp,tp->modules,tp_string_atom(tp, "sdl"),g);
	tp_obj g = tp_import(tp, tp_string_atom(tp, "sdl"), tp_None, tp_string_atom(tp, "<builtin>"));

	tp_set(tp,g,tp_string_atom(tp, "init_video"),tp_function(tp,_sdl_init_video));
	tp_set(tp,g,tp_string_atom(tp, "create_window"),tp_function(tp,_sdl_create_window));
	tp_set(tp,g,tp_string_atom(tp, "display_clear"),tp_function(tp,_sdl_display_clear));
	tp_set(tp,g,tp_string_atom(tp, "display_flip"),tp_function(tp,_sdl_display_flip));
	tp_set(tp,g,tp_string_atom(tp, "quit"),tp_function(tp,_sdl_quit));
}