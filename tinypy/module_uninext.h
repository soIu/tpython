CCore *UninextEngine=NULL;

tp_obj _uninext_engine(TP) {
	if (!UninextEngine) {
		UninextEngine = new CCore();
	}
	return tp_uninext_engine(UninextEngine);
}


void tp_module_uninext_init(TP) {
	tp_obj g = tp_import(tp, "uninext", "<builtin>");
	tp_set(tp,g, "Engine", tp_function(tp,_uninext_engine));
}
