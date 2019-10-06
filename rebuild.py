#!/usr/bin/python
import os, sys, subprocess

## Ubuntu Notes:
## sudo apt-get install g++-arm-linux-gnueabi gcc-arm-linux-gnueabi binutils-arm-linux-gnueabi


Makefile = '''
## note this Makefile is autogenerated by rebuild.py ##

TINYPYC=./tpc

VMLIB_FILES=tp.cpp dummy-compiler.cpp runtime.cpp <MODULES>
TPLIB_FILES=tp.cpp compiler.cpp runtime.cpp

#MODULES=math random re
#MODULES_A_FILES=$(MODULES:%=modules/%.a)
#MODULES_C_FILES=$(MODULES:%=modules/%/init.cpp)

#%.cpp : %.py
#	$(TINYPYC) -co $@ $^


%.o : %.cpp
	<CC> $(CFLAGS) <DEFINES> -std=c++11 <OPTIONS> <SDL_INCLUDE> -I . -c -o $@ $<

all: <EXE>

#modules/modules.c: $(MAKEFILE)
#	echo "#include <tinypy/tp.h>" > $@
#	for name in $(MODULES); do echo "void $${name}_init(TP);" >> $@; done
#	echo "void _tp_import_modules(TP) {" >> $@
#	for name in $(MODULES); do echo "$${name}_init(tp);" >> $@; done
#	echo "}" >> $@

#modules/modules.a: modules/modules.o \
#			$(MODULES_C_FILES:%.c=%.o)
#	$(AR) rcu $@ $^

tinypy/tp.o : tinypy/tp.cpp tinypy/tp*.cpp tinypy/tp*.h


# tpvm only takes compiled byte codes (.bytecode files)
#tpvm : $(VMLIB_FILES:%.c=tinypy/%.o) tinypy/vmmain.o modules/modules.a
<EXE> : $(VMLIB_FILES:%.cpp=tinypy/%.o) tinypy/vmmain.o
	<CC> <EXEOPTS> -o $@ $^ <LIBS>


clean:
	rm -rf <EXE>
	rm -rf tinypy/*.o
	#rm -rf modules/*/*.o
	#rm -rf modules/*.a
	#rm -rf modules/modules.cpp

'''

#gcc -c -Q -O3 --help=optimizers | grep enabled

def rebuild():
	mode = 'linux'
	exe = 'tpython++'
	exeopts = ''
	CC = 'c++'
	libs = '-lm -ldl -lpthread'
	defs = ''
	opts = ''
	mods = ''
	sdl_inc = ''
	embed_bytecode = False
	for arg in sys.argv[1:]:
		if arg.endswith('.py'):
			embed_bytecode = True
			defs += ' -DUSE_EMBEDDED_BYTECODE'
			subprocess.check_call([
				'./tpython++compiler.py', 
				'--beta', 
				'--gen-header=embedded_bytecode.gen.h', 
				arg
			])
			os.system('cp -v /tmp/embedded_bytecode.gen.h ./tinypy/.')
			break

	if '--cpython' in sys.argv:
		defs += ' -DUSE_PYTHON'
		libs += ' -lpython3.7m'
		opts += ' -I/usr/local/include/python3.7m'

	##############################################
	if '--wasm' in sys.argv or '--html' in sys.argv:
		mode = 'wasm'
		CC = os.path.expanduser('~/emsdk/fastcomp/emscripten/em++')
		libs = ''
		opts += ' -O3 -fno-rtti -s FILESYSTEM=0 -s DISABLE_EXCEPTION_CATCHING=0'
		if '--closure' in sys.argv:
			opts += ' --closure 1'

		if '--sdl' in sys.argv:  ## this is also required just at the linker stage
			opts += ' -s USE_SDL=2'
			if '--sdl-image' in sys.argv:
				opts += """ -s USE_SDL_IMAGE=2 -s SDL2_IMAGE_FORMATS='["png"]'"""
		if '--html' in sys.argv:
			exe += '.html'
		else:
			exe += '.js'
		if not embed_bytecode:
			print("WARN: you must embed a bytecode file to run TPython as WASM")
			print("run: ./rebuild.py myscript.py (this will generate and embed the bytecode)")
	elif '--arm' in sys.argv:
		CC = 'arm-linux-gnueabi-g++'
		defs = ''
		libs = '-ldl -lpthread'
		exe += '.arm'
		mode = 'arm'
		exeopts = '-static'
	elif '--windows' in sys.argv or '--mingw' in sys.argv:
		CC = 'x86_64-w64-mingw32-g++-posix'
		defs = ''
		libs = '-lpthread'
		exe += '.exe'
		mode = 'windows'
	else:  ## linux
		opts += ' -O3 -march=native -ffast-math -fno-math-errno -funsafe-math-optimizations -fno-signed-zeros -fno-trapping-math'

	if '--debug' in sys.argv:
		defs += ' -DDEBUG'
		opts += ' -g -rdynamic'
	elif mode == 'linux':
		#opts += ' -fno-exceptions'  ## TODO
		pass

	if '--sdl' in sys.argv:
		#mods += ' module_sdl.cpp'  # the entire sdl module is actually just in module_sdl.h
		defs += ' -DUSE_SDL'        # from runtime.cpp, module_sdl.h will be included
		if mode == 'wasm':
			#exeopts += """ -s USE_SDL=2 -s USE_SDL_IMAGE=2 -s SDL2_IMAGE_FORMATS='["png"]' -s TOTAL_MEMORY=33554432"""
			exeopts += ' -s USE_SDL=2'
			if '--sdl-image' in sys.argv:
				exeopts += """ -s USE_SDL_IMAGE=2 -s SDL2_IMAGE_FORMATS='["png"]'"""
			if '--allow-memory-growth' in sys.argv:
				exeopts += ' -s ALLOW_MEMORY_GROWTH=1'
		else:
			sdl_inc = '-I/usr/local/include'
			libs += ' -lSDL2'

	makefile = Makefile.replace("<CC>", CC).replace('<DEFINES>', defs).replace('<LIBS>', libs).replace('<EXE>', exe).replace('<EXEOPTS>', exeopts).replace('<OPTIONS>', opts).replace('<MODULES>', mods).replace('<SDL_INCLUDE>', sdl_inc)
	if mode=='windows':
		makefile = makefile.replace('-rdynamic', '')

	open('Makefile', 'wb').write(makefile)
	subprocess.check_call(['make', 'clean'])
	subprocess.check_call(['make'])

	if mode == 'windows':
		for dll in ['libstdc++-6.dll','libgcc_s_seh-1.dll', 'libwinpthread-1.dll']:
			if not os.path.isfile(dll):
				if dll == 'libwinpthread-1.dll':
					os.system('cp -v /usr/x86_64-w64-mingw32/lib/%s ./%s' %(dll, dll))
				else:
					os.system('cp -v /usr/lib/gcc/x86_64-w64-mingw32/5.3-posix/%s ./%s' %(dll, dll))

rebuild()