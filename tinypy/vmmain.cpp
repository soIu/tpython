// TODO option in Makefile for USE_PYTHON
#ifdef USE_PYTHON
	#include <Python.h>
#endif

#include "tp.h"
#include <thread>

#include <stdio.h>
#include <signal.h>
#include <stdlib.h>
#include <unistd.h>


#ifndef __MINGW64__
#include <execinfo.h>

// https://gist.github.com/fmela/591333
#include <dlfcn.h>    // for dladdr
#include <cxxabi.h>   // for __cxa_demangle
#include <cstdio>
#include <cstdlib>
// This function produces a stack backtrace with demangled function & method names.
std::string cpp_backtrace(int skip = 1)
{
		void *callstack[128];
		const int nMaxFrames = sizeof(callstack) / sizeof(callstack[0]);
		char buf[1024];
		int nFrames = backtrace(callstack, nMaxFrames);
		char **symbols = backtrace_symbols(callstack, nFrames);

		std::ostringstream trace_buf;
		for (int i = skip; i < nFrames; i++) {
				printf("%s\n", symbols[i]);

				Dl_info info;
				if (dladdr(callstack[i], &info) && info.dli_sname) {
						char *demangled = NULL;
						int status = -1;
						if (info.dli_sname[0] == '_')
								demangled = abi::__cxa_demangle(info.dli_sname, NULL, 0, &status);
						snprintf(buf, sizeof(buf), "%-3d %*p %s + %zd\n",
										 i, int(2 + sizeof(void*) * 2), callstack[i],
										 status == 0 ? demangled :
										 info.dli_sname == 0 ? symbols[i] : info.dli_sname,
										 (char *)callstack[i] - (char *)info.dli_saddr);
						free(demangled);
				} else {
						snprintf(buf, sizeof(buf), "%-3d %*p %s\n",
										 i, int(2 + sizeof(void*) * 2), callstack[i], symbols[i]);
				}
				trace_buf << buf;
		}
		free(symbols);
		if (nFrames == nMaxFrames)
				trace_buf << "[truncated]\n";
		return trace_buf.str();
}
#endif

// https://stackoverflow.com/questions/77005/how-to-automatically-generate-a-stacktrace-when-my-program-crashes
void crash_handler(int sig) {
	fprintf(stderr, "Error: signal %d:\n", sig);
	#ifdef __MINGW64__
		//void *array[10];
		//size_t size;
		// get void*'s for all entries on the stack
		//size = backtrace(array, 10);   // not supported in MINGW
		// print out all the frames to stderr, with unreadable names
		//backtrace_symbols_fd(array, size, STDERR_FILENO);
	#else
		std::cout << cpp_backtrace() << std::endl;
	#endif
	exit(1);
}

void * _tp_import_modules(TP);
/* from runtime */
tp_obj tp_load(TP, const char*);

void run_vm(int argc, char *argv[], int script_index){
	tp_vm *tp = tp_init(argc, argv);
	tp_obj fname = tp_string_atom(tp, argv[script_index]);
	tp_obj code = tp_load(tp, argv[script_index]);
	try {
		tp_obj module = tp_import(tp, tp_string_atom(tp, "__main__"), code, fname);
	} catch (const char * str) {
		std::cout << "Runtime Exception: " << str << std::endl;
		crash_handler(-1);
	}
	tp_deinit(tp);
}

int main(int argc,  char *argv[]) {
	signal(SIGSEGV, crash_handler); // memory segfault
	signal(SIGABRT, crash_handler); // some old places in tinypy code had used `abort()`
	signal(SIGINT, crash_handler);  // allow CTRL+C to halt the program

#ifdef USE_PYTHON
	Py_SetStandardStreamEncoding("utf-8", "surrogateescape");
	Py_Initialize();
#endif

	if (argc==1){
		std::cout << "Error: no byte code file provided" << std::endl;
	} else if (argc==2){
		run_vm(argc, argv, 1);
	} else if (argc==3) {
		std::thread t1( [=]{run_vm(argc, argv, 1);} );
		std::thread t2( [=]{run_vm(argc, argv, 2);} );
		t1.join();
		t2.join();
	} else {
		std::cout << "TODO: more than two threads it not yet supported" << std::endl;
	}

	return 0;
}
