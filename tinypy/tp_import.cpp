tp_obj tp_import(TP, tp_obj name, tp_obj code, tp_obj fname) {
	tp_obj g;

	g = tp_interface_t(tp);
	tp_set(tp, g, tp_string_atom(tp, "__name__"), name);
	tp_set(tp, g, tp_string_atom(tp, "__file__"), fname);
	//tp_set(tp, g, tp_string_atom(tp, "__code__"), code);
	tp_set(tp, g, tp_string_atom(tp, "__dict__"), g);

	tp_set(tp, tp->modules, name, g);

	/* an older versoin of the code does not run frame of jmp == 0. Why?*/
	/*
	 tp_enter_frame(tp, globals, code, &r);
	 if (!tp->jmp) {
		 tp_run_frame(tp);
	 } 
	 * */
	if (code.type.type_id != TP_NONE) {
		tp_exec(tp, code, g);
	} else {
		#ifdef DEBUG
			std::cout << "WARN: code.type.type_id=" << code.type.type_id << std::endl;
		#endif
		//throw "empty module";
	}

	return g;
}

/* Function: tp_import
 * Imports a module.
 * 
 * Parameters:
 * fname - The filename of a file containing the module's code.
 * name - The name of the module.
 * codes - The module's code.  If this is given, fname is ignored.
 * len - The length of the bytecode.
 *
 * Returns:
 * The module object.
 */
tp_obj tp_import_from_buffer(TP, const char * fname, const char * name, void *codes, int len) {
	#ifdef DEBUG
		std::cout << "tp_import.cpp tp_import_from_buffer:" << std::endl;
		std::cout << fname << std::endl;
		std::cout << name << std::endl;
		std::cout << len << std::endl;
	#endif

	tp_obj f = fname?tp_string_atom(tp, fname):tp_None;
	tp_obj bc = codes?tp_string_t_from_const(tp, (const char*)codes, len):tp_None;
	return tp_import(tp, tp_string_atom(tp, name), bc, f);
}

// used by runtime.cpp import corelib
tp_obj tp_import_from_buffer(TP, const char * name, unsigned char *codes, int len) {
	#ifdef DEBUG
		std::cout << "tp_import.cpp tp_import_from_buffer: corelib" << std::endl;
		std::cout << "	module name: " << name << std::endl;
		std::cout << "	modules bytes:" << len << std::endl;
	#endif

	tp_obj f = tp_None;
	tp_obj bc = tp_string_t_from_const(tp, (const char*)codes, len);
	//return tp_import(tp, tp_string_atom(tp, name), bc, f);
	//std::string s = std::string(  reinterpret_cast< char const* >(codes), len);
	//tp_obj bc = tp_string_from_stdstring(tp, s);  // TODO fix bug in tp_string_from_stdstring
	//if (bc.type.type_id == TP_NONE) {
	//	throw "unable to convert byte code to a tp_string";
	//} else {
	//	std::cout << "load bytecode OK" << std::endl;
	//}

	#if DEBUG > 3
		std::cout << s << std::endl;
	#endif

	return tp_import(tp, tp_string_atom(tp, name), bc, f);
}

