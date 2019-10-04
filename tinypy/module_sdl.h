#include <SDL2/SDL.h>

#define _SDL_TYPE_SURF 0x1001

tp_obj _sdl_init_video(TP) {
	if (SDL_Init(SDL_INIT_VIDEO) < 0)
		std::cout << "WARN: could not init sdl video" << std::endl;
	return tp_None;
}


tp_obj _sdl_surf_to_obj(TP,SDL_Surface *s) {
	tp_obj self = tp_dict(tp);
	tp_obj d = tp_data(tp,_SDL_TYPE_SURF,s);
	//d.data.info->free = pygame_surf_free;
	tp_set(tp,self,tp_string_atom(tp, "__surface__"),d);
	//tp_set(tp,self,tp_string_atom(tp, "set_at"),tp_method(tp,self,pygame_surface_set_at));
	return self;
}

SDL_Window *_sdl_window = NULL;

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

	SDL_Surface *s = SDL_GetWindowSurface(_sdl_window);
	if (!s)
		std::cout << "WARN: could not get sdl surface from window" << std::endl;

	return _sdl_surf_to_obj(tp,s);
}

void tp_module_sdl_init(TP) {
	tp_obj g,m;
	g = tp_dict(tp);
	tp_set(tp,tp->modules,tp_string_atom(tp, "sdl"),g);
	tp_set(tp,g,tp_string_atom(tp, "init_video"),tp_function(tp,_sdl_init_video));
	tp_set(tp,g,tp_string_atom(tp, "create_window"),tp_function(tp,_sdl_create_window));

}