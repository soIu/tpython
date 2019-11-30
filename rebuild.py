#!/usr/bin/python
import os, sys, subprocess, random, json

## Ubuntu Notes:
## sudo apt-get install g++-arm-linux-gnueabi gcc-arm-linux-gnueabi binutils-arm-linux-gnueabi


def gen_interpreter_codes(randomize=False):
	## this is default in order of the switch/case main interp loop in tp_vm.cpp,
	## randomizing this could have some affect on branch prediction, or how gcc optimizes the switch/case
	codes = [
		'REGS','NAME','INTEGER','NUMBER','STRING','MOVE',
		'IF','EQ','LE','LT', 'GGET','GSET',
		'ADD','SUB','MUL','DIV','CMP','MGET','GET','SET',
		'NE','NOT','IFN','ITER','HAS','IGET','DEL','IFACE',
		'DICT','LIST','PARAMS','LEN','JUMP','SETJMP','CALL',
		'DEF','RETURN','RAISE','NONE','MOD','LSH','RSH', 
		'POW','BITAND','BITOR','BITNOT','BITXOR',  
		'PASS','FILE','DEBUG',
		'LINE',
	]
	## note: POS is TP_ILINE in tp_vm.cpp
	if randomize:
		random.shuffle(codes)

	## note: EOF must always be first
	codes = ['EOF'] + codes

	enums = ['TP_I'+a for a in codes]
	enums.append('TP_ITOTAL')
	tp_vm_enums = 'enum {%s};' % ','.join(enums)
	tp_vm_debug_strings = 'const char *tp_strings[TP_ITOTAL] = {%s};' % ','.join(['"%s"' %a for a in codes])
	open('./tinypy/interpreter_codes.gen.h', 'wb').write(tp_vm_enums)
	open('./tinypy/interpreter_codes_debug.gen.h', 'wb').write(tp_vm_debug_strings)

	encode_py = '%s = range(%s)' %(','.join(codes), len(codes))
	open('./tinypy/compiler/interpreter_codes_gen.py', 'wb').write(encode_py)

BlendotTypesFiles = '''blendot/mutex.cpp blendot/memory.gen.cpp blendot/pool_allocator.cpp blendot/pool_vector.cpp blendot/message_queue.cpp blendot/object.gen.cpp blendot/node_path.cpp blendot/ip_address.cpp blendot/class_db.cpp blendot/resource.cpp blendot/method_bind.cpp blendot/reference.gen.cpp blendot/ref_ptr.cpp blendot/array.gen.cpp blendot/variant_op.cpp blendot/variant.cpp blendot/string_name.cpp blendot/print_string.cpp blendot/core_string_names.cpp blendot/dictionary.cpp blendot/ustring.cpp blendot/math_funcs.cpp blendot/basis.gen.cpp blendot/vector2.gen.cpp blendot/vector3.gen.cpp blendot/quat.gen.cpp blendot/color.gen.cpp blendot/aabb.gen.cpp blendot/transform.gen.cpp blendot/transform_2d.gen.cpp blendot/rect2.gen.cpp blendot/rid.gen.cpp blendot/scene/main/scene_tree.cpp blendot/scene/main/node.cpp blendot/scene/3d/spatial.gen.cpp blendot/scene/scene_string_names.cpp blendot/main_loop.gen.cpp blendot/engine.gen.cpp blendot/scene/resources/material.cpp blendot/scene/resources/mesh.gen.cpp blendot/scene/resources/surface_tool.cpp blendot/face3.gen.cpp blendot/plane.gen.cpp blendot/scene/resources/shape.cpp blendot/quick_hull.cpp blendot/scene/resources/convex_polygon_shape.cpp blendot/scene/resources/concave_polygon_shape.cpp blendot/triangle_mesh.cpp blendot/servers/visual_server.cpp blendot/image.cpp blendot/geometry.gen.cpp blendot/servers/visual/visual_server_raster.cpp blendot/servers/visual/visual_server_globals.cpp blendot/servers/visual/rasterizer.cpp'''


Makefile = '''
## note this Makefile is autogenerated by rebuild.py ##

TINYPYC=./tpc

VMLIB_FILES=tp.gen.cpp dummy-compiler.cpp runtime.gen.cpp <MODULES>
TPLIB_FILES=tp.gen.cpp compiler.cpp runtime.gen.cpp

#MODULES=math random re
#MODULES_A_FILES=$(MODULES:%=modules/%.a)
#MODULES_C_FILES=$(MODULES:%=modules/%/init.cpp)

#%.cpp : %.py
#	$(TINYPYC) -co $@ $^


%.o : %.cpp
	<CC> $(CFLAGS) <DEFINES> -std=c++11 <OPTIONS> <SDL_INCLUDE> -I .  -I ./tinypy/blendot -c -o $@ $<

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

tinypy/tp.o : tinypy/tp.gen.cpp tinypy/tp*.cpp tinypy/tp*.h


# tpvm only takes compiled byte codes (.bytecode files)
#tpvm : $(VMLIB_FILES:%.c=tinypy/%.o) tinypy/vmmain.o modules/modules.a
<EXE> : $(VMLIB_FILES:%.cpp=tinypy/%.o) tinypy/vmmain.gen.o
	<CC> <EXEOPTS> -o $@ $^ <LIBS>


clean:
	rm -rf <EXE>
	rm -rf tinypy/*.o

'''

CMakeFile = '''
cmake_minimum_required(VERSION 3.8)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
add_definitions(%s)
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
project (tinypy)
include(${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake OPTIONAL RESULT_VARIABLE HAS_CONAN)
conan_basic_setup()
include(os)
os_add_executable(tpythonos "TPythonOS" tp.gen.cpp dummy-compiler.cpp runtime.gen.cpp vmmain.gen.cpp)
#os_add_drivers(tpythonos virtionet vmxnet3 boot_logger)
os_add_stdout(tpythonos default_stdout)
'''

#gcc -c -Q -O3 --help=optimizers | grep enabled

def parse_exe_symbols():
	symbols = subprocess.check_output(['strings', './tpython++'])
	ret = []
	for name in symbols.splitlines():
		if name.startswith('_Z') and '.' not in name:
			ret.append(name)
	return ret

def gen_interpreter(stage=None):
	cmd = [
		'./tpython++compiler.py', 
		'./tinypy'
	]
	if '--debug' in sys.argv:
		cmd.append('--debug')
	if '--secure' in sys.argv:
		cmd.append('--secure')
	if '--secure-binary' in sys.argv:
		cmd.append('--secure')
		cmd.append('--secure-binary')
		if stage==2:
			cmd.append( json.dumps(parse_exe_symbols()) )  ## generated at stage 1
			cmd.append( '/tmp/tinypy.json' )  ## generated at stage 1
	#print(cmd)
	subprocess.check_call(cmd)

def rebuild(stage=None):
	os.system('rm -f tinypy/__user_bytecode__.gen.h')
	os.system('rm -f tinypy/__user_pythonic__.gen.h')
	os.system('rm -f tinypy/__user_pythonic__.pyh')
	os.system('rm -f tinypy/*.gcda')
	if stage is None or stage < 2:
		os.system('rm -f /tmp/tinypy.json')

	gen_interpreter_codes( randomize='--secure' in sys.argv)

	mode = 'linux'
	exe = 'tpython++'
	exeopts = ''

	CC = 'c++'
	libs = '-lm -ldl -lpthread'

	if '--no-blendot' in sys.argv or '--includeos' in sys.argv:
		defs = ''
		mods = ''
	else:
		defs = '-DBLENDOT_TYPES'
		mods = BlendotTypesFiles
	opts = ''

	if '--shared' in sys.argv:
		exe = 'libtpython++.so'
		exeopts = '-shared -fPIC '
		opts = '-fPIC '
		defs += ' -DSHAREDLIB'

	sdl_inc = ''
	embed_bytecode = False
	unreal_plugin = None
	unreal_ver = None
	unreal_project = os.path.expanduser('~/Documents/Unreal Projects/TPythonPluginTest')
	for arg in sys.argv[1:]:
		if arg.endswith('.py'):
			embed_bytecode = True
			defs += ' -DUSE_EMBEDDED_BYTECODE'
			cmd = [
				'./tpython++compiler.py', 
				'--beta', 
				'--gen-header=embedded_bytecode.gen.h', 
				arg
			]
			if '--debug' in sys.argv:
				cmd.append('--debug')
			subprocess.check_call(cmd)
			os.system('cp -v /tmp/embedded_bytecode.gen.h ./tinypy/__user_bytecode__.gen.h')
			if os.path.isfile('./tinypy/__user_pythonic__.pyh'):
				defs += ' -DUSE_USER_CUSTOM_CPP'
			break
		elif arg.endswith('.unreal'):
			unreal_plugin = arg
			#mode = 'unreal'
		elif os.path.isdir(arg):
			unreal_project = arg
		elif arg.startswith('--unreal-'):
			if arg.startswith('--unreal-version='):
				unreal_ver = arg

	gen_interpreter(stage=stage)


	if '--cpython' in sys.argv:
		defs += ' -DUSE_PYTHON'
		libs += ' -lpython3.7m'
		opts += ' -I/usr/local/include/python3.7m'

	##############################################
	if '--includeos' in sys.argv:
		mode = 'includeos'
		if not os.path.isdir('./tpythonos_build'):
			os.mkdir('tpythonos_build')
			subprocess.check_call(['conan', 'install', '../tinypy', '-pr', 'clang-6.0-linux-x86_64'], cwd='./tpythonos_build')
	elif '--wasm' in sys.argv or '--html' in sys.argv:
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
	elif '--android' in sys.argv:
		print('ensure that you have installed android sdk28 and build-tools28')
		print('sudo ./sdkmanager  "platforms;android-28" "build-tools;28.0.0"')
		mode = 'android'
		if '--sdl' not in sys.argv:
			raise RuntimeError('SDL is required for Android build, enable with `--sdl`')
		sdlroot = os.path.expanduser('~/SDL2-2.0.9')
		#sdlroot = os.path.expanduser('~/sdl2-android-example')
		#if not os.path.isdir(sdlroot):
		#	subprocess.check_call(
		#		['git', 'clone', 'https://github.com/georgik/sdl2-android-example.git'],
		#		cwd=os.path.expanduser('~/')
		#	)
		#if not os.path.isdir(sdlroot):
		#	raise RuntimeError('unable to git clone from: https://github.com/georgik/sdl2-android-example.git')

	else:  ## linux
		if '--secure-binary' in sys.argv:
			opts += ' -O2 -finline-small-functions -march=native'
		else:
			opts += ' -O3 -funroll-loops -finline-small-functions -march=native -ffast-math -fno-math-errno -funsafe-math-optimizations -fno-signed-zeros -fno-trapping-math -frename-registers'
		exeopts += opts
		if '--gcc5' in sys.argv:
			CC = '/usr/bin/g++-5'
			assert os.path.isfile(CC)

	###############################
	if '--debug' in sys.argv:
		defs += ' -DDEBUG'
		opts += ' -g -rdynamic'
	elif mode == 'linux':
		#opts += ' -fno-exceptions'  ## TODO
		pass
	if '--secure-binary' in sys.argv:
		if '-rdynamic' not in opts:
			opts += ' -rdynamic'
		exeopts += ' -fPIC -Wl,--export-dynamic'

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

	if unreal_plugin:
		if not os.path.isdir(unreal_project):
			os.makedirs( unreal_project )
		cmd = [
			'./tpython++compiler.py', 
			'--beta', 
			'--unreal'
		]
		if unreal_ver:
			cmd.append(unreal_ver)
		cmd.extend([
			unreal_plugin,
			unreal_project,
		])
		subprocess.check_call(cmd)

	elif mode == 'includeos':
		if not embed_bytecode:
			raise RuntimeError('includeos builds require that you embed your bytecode')

		os.system('rm -f ./tpythonos_build/CMakeFiles/tpythonos.elf.bin.dir/*.o')

		#subprocess.check_call(['bash', '-c', 'source activate.sh'], cwd='./tpythonos_build')  ## this will not work
		env = {}
		for ln in open('./tpythonos_build/activate.sh','rb').read().splitlines():
			if ln.startswith( ('export ', 'PS1=', 'OLD_PS1=') ):
				continue
			else:
				assert '=' in ln
				ename  = ln[ : ln.index('=') ]
				evalue = ln[ ln.index('"')+1 : ln.rindex('"') ]
				if ename == 'PATH':
					evalue = '%s:%s' %(evalue, os.environ['PATH'])
				env[ename] = evalue
		print(env)

		cmd = ['cmake', '-DCMAKE_C_COMPILER=clang-6.0', '-DCMAKE_CXX_COMPILER=clang++-6.0']
		cmd.append('../tinypy')
		print(cmd)
		cmakedefs = ['-DINCLUDEOS']
		for d in defs.split():
			cmakedefs.append(d)
		assert '-DUSE_EMBEDDED_BYTECODE' in cmakedefs

		vmjson = {"mem":128, "net":[]}
		if '--vga' in sys.argv:
			vmjson["vga"] = "std"
			cmakedefs.append('-DINCLUDEOS_VGA')
		elif '--svga' in sys.argv:
			vmjson["vga"] = "qxl"
			cmakedefs.append('-DINCLUDEOS_SVGA')

		open('./tinypy/vm.json', 'wb').write(json.dumps(vmjson))

		cmakedefs = ' '.join(cmakedefs)
		cmakefile = CMakeFile % cmakedefs
		open('./tinypy/CMakeLists.txt', 'wb').write(cmakefile)


		subprocess.check_call(cmd, cwd='./tpythonos_build', env=env)
		subprocess.check_call(['cmake', '--build', '.'], cwd='./tpythonos_build', env=env)
		#subprocess.check_call(['boot', 'tpythonos'], cwd='./tpythonos_build', env=env)
		print('tpythonos build OK - to test run these commands:')
		print('cd tpythonos_build')
		print('source activate.sh')
		print('boot tpythonos')

	elif mode == 'android':
		androbuildsh = os.path.join(sdlroot, 'build-scripts/androidbuild.sh')
		assert os.path.isfile(androbuildsh)
		c_files = [
			'./tinypy/tp.cpp',
			'./tinypy/dummy-compiler.cpp',
			'./tinypy/runtime.cpp',
		]
		subprocess.check_call([androbuildsh, 'org.tpython.helloworld'] + c_files)
		gradlew = os.path.join(sdlroot, 'build/org.tpython.helloworld/gradlew')
		subprocess.check_call([gradlew, 'installDebug'])

	elif '--pgo' in sys.argv:
		makefile_gen_pgo = Makefile.replace("<CC>", CC).replace('<DEFINES>', defs).replace('<LIBS>', libs).replace('<EXE>', exe).replace('<EXEOPTS>', ' -fprofile-generate ' + exeopts).replace('<OPTIONS>', ' -fprofile-generate ' + opts).replace('<MODULES>', mods).replace('<SDL_INCLUDE>', sdl_inc)
		makefile_use_pgo = Makefile.replace("<CC>", CC).replace('<DEFINES>', defs).replace('<LIBS>', libs).replace('<EXE>', exe).replace('<EXEOPTS>', ' -fprofile-use ' + exeopts).replace('<OPTIONS>', ' -fprofile-use ' + opts).replace('<MODULES>', mods).replace('<SDL_INCLUDE>', sdl_inc)

		open('Makefile', 'wb').write(makefile_gen_pgo)
		subprocess.check_call(['make', 'clean'])
		subprocess.check_call(['make'])
		subprocess.check_call(['./tpython++'])

		open('Makefile', 'wb').write(makefile_use_pgo)
		subprocess.check_call(['make', 'clean'])
		subprocess.check_call(['make'])

	else:
		makefile = Makefile.replace("<CC>", CC).replace('<DEFINES>', defs).replace('<LIBS>', libs).replace('<EXE>', exe).replace('<EXEOPTS>', exeopts).replace('<OPTIONS>', opts).replace('<MODULES>', mods).replace('<SDL_INCLUDE>', sdl_inc)
		if mode=='windows':
			makefile = makefile.replace('-rdynamic', '')

		open('Makefile', 'wb').write(makefile)
		subprocess.check_call(['make', 'clean'])
		subprocess.check_call(['make'])

	#####################
	if mode == 'windows':
		for dll in ['libstdc++-6.dll','libgcc_s_seh-1.dll', 'libwinpthread-1.dll']:
			if not os.path.isfile(dll):
				if dll == 'libwinpthread-1.dll':
					os.system('cp -v /usr/x86_64-w64-mingw32/lib/%s ./%s' %(dll, dll))
				else:
					os.system('cp -v /usr/lib/gcc/x86_64-w64-mingw32/5.3-posix/%s ./%s' %(dll, dll))


def main():
	if '--clean' in sys.argv:
		os.system('rm -rf tinypy/*.fodg')
		os.system('rm -rf tinypy/blendot/*.fodg')
		os.system('rm -rf tinypy/blendot/*.o')
		os.system('rm -rf tinypy/blendot/servers/*.fodg')
		os.system('rm -rf tinypy/blendot/servers/*.o')
		os.system('rm -rf tinypy/blendot/servers/visual/*.fodg')
		os.system('rm -rf tinypy/blendot/servers/visual/*.o')
		os.system('rm -rf tinypy/blendot/scene/*.fodg')
		os.system('rm -rf tinypy/blendot/scene/*.o')
		os.system('rm -rf tinypy/blendot/scene/3d/*.fodg')
		os.system('rm -rf tinypy/blendot/scene/3d/*.o')
		os.system('rm -rf tinypy/blendot/scene/main/*.fodg')
		os.system('rm -rf tinypy/blendot/scene/main/*.o')
		os.system('rm -rf tinypy/blendot/scene/resources/*.fodg')
		os.system('rm -rf tinypy/blendot/scene/resources/*.o')

	if '--secure-binary' in sys.argv:
		rebuild(stage=1)
		rebuild(stage=2)
	else:
		rebuild()

main()