#include "tp.h"
#include <thread>

#include <stdio.h>
#include <execinfo.h>
#include <signal.h>
#include <stdlib.h>
#include <unistd.h>

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

// https://stackoverflow.com/questions/77005/how-to-automatically-generate-a-stacktrace-when-my-program-crashes
void crash_handler(int sig) {
	//void *array[10];
	//size_t size;
	// get void*'s for all entries on the stack
	//size = backtrace(array, 10);
	// print out all the frames to stderr, with unreadable names
	fprintf(stderr, "Error: signal %d:\n", sig);
	//backtrace_symbols_fd(array, size, STDERR_FILENO);
	std::cout << cpp_backtrace() << std::endl;
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
	signal(SIGSEGV, crash_handler);
	signal(SIGABRT, crash_handler);
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
