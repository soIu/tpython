/*************************************************************************/
/*  visual_server_raster.cpp                                             */
/*************************************************************************/
/*                       This file is part of:                           */
/*                           GODOT ENGINE                                */
/*                      https://godotengine.org                          */
/*************************************************************************/
/* Copyright (c) 2007-2019 Juan Linietsky, Ariel Manzur.                 */
/* Copyright (c) 2014-2019 Godot Engine contributors (cf. AUTHORS.md)    */
/*                                                                       */
/* Permission is hereby granted, free of charge, to any person obtaining */
/* a copy of this software and associated documentation files (the       */
/* "Software"), to deal in the Software without restriction, including   */
/* without limitation the rights to use, copy, modify, merge, publish,   */
/* distribute, sublicense, and/or sell copies of the Software, and to    */
/* permit persons to whom the Software is furnished to do so, subject to */
/* the following conditions:                                             */
/*                                                                       */
/* The above copyright notice and this permission notice shall be        */
/* included in all copies or substantial portions of the Software.       */
/*                                                                       */
/* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,       */
/* EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF    */
/* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.*/
/* IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY  */
/* CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,  */
/* TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE     */
/* SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                */
/*************************************************************************/

#include "visual_server_raster.h"
#ifdef BLENDOT
	#include "core/io/marshalls.h"
	#include "core/os/os.h"
	#include "core/project_settings.h"
#endif
#include "sort_array.h"
#include "visual_server_canvas.h"
#include "visual_server_globals.h"
#include "visual_server_scene.h"

// careful, these may run in different threads than the visual server

int VisualServerRaster::changes = 0;

/* BLACK BARS */

void VisualServerRaster::black_bars_set_margins(int p_left, int p_top, int p_right, int p_bottom) {
#ifdef BLENDOT
	black_margin[MARGIN_LEFT] = p_left;
	black_margin[MARGIN_TOP] = p_top;
	black_margin[MARGIN_RIGHT] = p_right;
	black_margin[MARGIN_BOTTOM] = p_bottom;
#endif
}

void VisualServerRaster::black_bars_set_images(RID p_left, RID p_top, RID p_right, RID p_bottom) {
#ifdef BLENDOT
	black_image[MARGIN_LEFT] = p_left;
	black_image[MARGIN_TOP] = p_top;
	black_image[MARGIN_RIGHT] = p_right;
	black_image[MARGIN_BOTTOM] = p_bottom;
#endif
}

void VisualServerRaster::_draw_margins() {
#ifdef BLENDOT
	VSG::canvas_render->draw_window_margins(black_margin, black_image);
#endif
};

/* FREE */

void VisualServerRaster::free(RID p_rid) {
#ifdef BLENDOT
	if (VSG::storage->free(p_rid))
		return;
	if (VSG::canvas->free(p_rid))
		return;
	if (VSG::viewport->free(p_rid))
		return;
	if (VSG::scene->free(p_rid))
		return;
	if (VSG::scene_render->free(p_rid))
		return;
#endif
}

/* EVENT QUEUING */

void VisualServerRaster::request_frame_drawn_callback(Object *p_where, const StringName &p_method, const Variant &p_userdata) {
#ifdef BLENDOT
	ERR_FAIL_NULL(p_where);
	FrameDrawnCallbacks fdc;
	fdc.object = p_where->get_instance_id();
	fdc.method = p_method;
	fdc.param = p_userdata;
	frame_drawn_callbacks.push_back(fdc);
#endif
}

void VisualServerRaster::draw(bool p_swap_buffers, double frame_step) {
#ifdef BLENDOT

	//needs to be done before changes is reset to 0, to not force the editor to redraw
	VS::get_singleton()->emit_signal("frame_pre_draw");

	changes = 0;

	VSG::rasterizer->begin_frame(frame_step);

	VSG::scene->update_dirty_instances(); //update scene stuff

	VSG::viewport->draw_viewports();
	VSG::scene->render_probes();
	_draw_margins();
	VSG::rasterizer->end_frame(p_swap_buffers);

	while (frame_drawn_callbacks.front()) {

		Object *obj = ObjectDB::get_instance(frame_drawn_callbacks.front()->get().object);
		if (obj) {
			Variant::CallError ce;
			const Variant *v = &frame_drawn_callbacks.front()->get().param;
			obj->call(frame_drawn_callbacks.front()->get().method, &v, 1, ce);
			if (ce.error != Variant::CallError::CALL_OK) {
				String err = Variant::get_call_error_text(obj, frame_drawn_callbacks.front()->get().method, &v, 1, ce);
				ERR_PRINTS("Error calling frame drawn function: " + err);
			}
		}

		frame_drawn_callbacks.pop_front();
	}
	VS::get_singleton()->emit_signal("frame_post_draw");
#endif
}
void VisualServerRaster::sync() {}

bool VisualServerRaster::has_changed() const {
#ifdef BLENDOT
	return changes > 0;
#endif
}
void VisualServerRaster::init() {
#ifdef BLENDOT
	VSG::rasterizer->initialize();
#endif
}
void VisualServerRaster::finish() {
#ifdef BLENDOT
	if (test_cube.is_valid()) {
		free(test_cube);
	}

	VSG::rasterizer->finalize();
#endif
}

/* STATUS INFORMATION */

int VisualServerRaster::get_render_info(RenderInfo p_info) {
#ifdef BLENDOT
	return VSG::storage->get_render_info(p_info);
#endif
}

/* TESTING */

void VisualServerRaster::set_boot_image(const Ref<Image> &p_image, const Color &p_color, bool p_scale, bool p_use_filter) {
#ifdef BLENDOT
	redraw_request();
	VSG::rasterizer->set_boot_image(p_image, p_color, p_scale, p_use_filter);
#endif
}
void VisualServerRaster::set_default_clear_color(const Color &p_color) {
#ifdef BLENDOT
	VSG::viewport->set_default_clear_color(p_color);
#endif
}

bool VisualServerRaster::has_feature(Features p_feature) const {
	return false;
}

RID VisualServerRaster::get_test_cube() {
#ifdef BLENDOT
	if (!test_cube.is_valid()) {
		test_cube = _make_test_cube();
	}
	return test_cube;
#endif
}

bool VisualServerRaster::has_os_feature(const String &p_feature) const {
#ifdef BLENDOT
	return VSG::storage->has_os_feature(p_feature);
#endif
}

void VisualServerRaster::set_debug_generate_wireframes(bool p_generate) {
#ifdef BLENDOT
	VSG::storage->set_debug_generate_wireframes(p_generate);
#endif
}

void VisualServerRaster::call_set_use_vsync(bool p_enable) {
#ifdef BLENDOT
	OS::get_singleton()->_set_use_vsync(p_enable);
#endif
}

bool VisualServerRaster::is_low_end() const {
#ifdef BLENDOT
	return VSG::rasterizer->is_low_end();
#endif
}
VisualServerRaster::VisualServerRaster() {
	std::cout << "making new VisualServerRaster" << std::endl;
	std::cout << this << std::endl;
	singleton = this;

#ifdef BLENDOT
	VSG::canvas = memnew(VisualServerCanvas);
	VSG::viewport = memnew(VisualServerViewport);
	VSG::scene = memnew(VisualServerScene);
	VSG::rasterizer = Rasterizer::create();  // where is the create func set?
	VSG::storage = VSG::rasterizer->get_storage();  // just an RID container?
	VSG::canvas_render = VSG::rasterizer->get_canvas();
	VSG::scene_render = VSG::rasterizer->get_scene();
	for (int i = 0; i < 4; i++) {
		black_margin[i] = 0;
		black_image[i] = RID();
	}
#endif
}

VisualServerRaster::~VisualServerRaster() {
#ifdef BLENDOT
	memdelete(VSG::canvas);
	memdelete(VSG::viewport);
	memdelete(VSG::rasterizer);
	memdelete(VSG::scene);
#endif
}
