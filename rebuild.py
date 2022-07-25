#!/usr/bin/python
import os, sys, subprocess, random, json, base64, shutil

# always generate code relative to this file.
workspace_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(workspace_dir)

## Ubuntu Notes:
## sudo apt-get install g++-arm-linux-gnueabi gcc-arm-linux-gnueabi binutils-arm-linux-gnueabi

def install_emsdk():
	return
	subprocess.check_call(['git', 'clone', 'https://github.com/emscripten-core/emsdk.git'], cwd=os.path.expanduser('~/'))
	subprocess.check_call(['./emsdk', 'install', 'latest-upstream'], cwd=os.path.expanduser('~/emsdk'))
	subprocess.check_call(['./emsdk', 'activate', 'latest-upstream'], cwd=os.path.expanduser('~/emsdk'))

## https://developer.mozilla.org/en-US/docs/Web/API/Node/textContent
SIMPLE_JS_EDITOR = '''
<script>
function tpy_recompile() {
	var pre = document.getElementById("TPY_SRC");
	//kills new lines from br nodes//var src = pre.textContent;
	var src = pre.innerHTML;
	var oReq = new XMLHttpRequest();
	oReq.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			document.body.innerHTML = this.responseText;
		}
	};
	oReq.open("GET", "/recompile?" + btoa(src));
	oReq.send();
	document.body.innerHTML = "compiling, please wait...";
}
</script>
<hr/>
<button onclick="javascript:tpy_recompile()">compile</button>
<a href="/">reload</a>

'''

PAKO_MISSING = '''

WARN: Could not find the pako source folder in your home directory,
try running the commands below, and then rebuild.

	cd
	git clone https://github.com/nodeca/pako.git

'''

EMHACK = '''
// EMSCRIPTEN_START_ASM
var asm =Module["asm"]// EMSCRIPTEN_END_ASM
(asmGlobalArg, asmLibraryArg, buffer);
'''.strip()

EMHACK_NEW = '''
// EMSCRIPTEN_START_ASM
Module["asm"](asmGlobalArg, asmLibraryArg, buffer, function after_wasm_load(asm) {
'''

EMHACK_INIT = '''
var info = {'env': env, 'global': {'NaN': NaN, 'Infinity': Infinity }, 'global.Math': Math, 'asm2wasm': asm2wasmImports};
var wasm = WebAssembly.instantiate(pako.inflate(atob("%s")),info);
console.log(wasm);
wasm.then( function (result){
	Module["asm"]=result.instance.exports;
	callback(Module.asm);  // init global ctors //
	//for (var i=0; i<Module.preRun.length; i++)
	//	Module.preRun[i]();
	run();
}); 


var exports = {};
'''

EMHACK_FS_HEAD = '''
(function() {
 var loadPackage = function(metadata) {

  function runWithFS() {
'''.strip()

COMPRESSION_MAPPING = {
	"a":255,
	"b":188,
	"c":173,
	"d":168,
	"e":116,
	"f":200,
	"g":241,
	"h":136,
	"i":252,
	"j":249,
	"k":152,
	"l":128,
	"m":176,
	"n":151,
	"o":172,
	"p":217,
	"q":216,
	"r":236,
	"s":174,
	"t":153,
	"u":228,
	"v":240,
	"w":208,
	"x":165,
	"y":199,
	"z":185,
}

EMHACK_FS_HEAD_NEW = '''
function runWithFS() {
	var %s;
	%s
''' % (
		','.join(COMPRESSION_MAPPING.keys()),
		';'.join(['%s=%s' %(key,COMPRESSION_MAPPING[key]) for key in COMPRESSION_MAPPING])
	)

EMHACK_FS_TAIL = '''
  if (Module['calledRun']) {
    runWithFS();
  } else {
    if (!Module['preRun']) Module['preRun'] = [];
    Module["preRun"].push(runWithFS); // FS is not initialized yet, wait for it
  }

 }
 loadPackage({"files": []});

})();
'''.strip()

def pakoify(js, exe='tpython++', wasmgz=None):
	assert exe in js
	js = js.replace("'%s.wasm'" %exe, "'%s.wasm.gz'" %exe)
	#assert js.count('(xhr.response)')==2
	#js = js.replace('(xhr.response)')
	assert js.count('return WebAssembly.instantiate(binary, info);') == 1
	assert js.count('var exports = createWasm(env);') == 1
	assert js.count("Module['preRun'] = [];") == 2
	assert js.count("var Module = typeof Module !== 'undefined' ? Module : {};") == 1

	assert js.count('function __registerKeyEventCallback(target, userData, useCapture, callbackfunc, eventTypeId, eventTypeString, targetThread) {') == 1
	js = js.replace(
		'function __registerKeyEventCallback(target, userData, useCapture, callbackfunc, eventTypeId, eventTypeString, targetThread) {',
		'function __registerKeyEventCallback(target, userData, useCapture, callbackfunc, eventTypeId, eventTypeString, targetThread) { return;'
	)

	assert js.count(EMHACK_FS_HEAD)==1
	assert js.count(EMHACK_FS_TAIL)==1

	js = js.replace(EMHACK_FS_HEAD, EMHACK_FS_HEAD_NEW).replace(EMHACK_FS_TAIL, '')

	assert js.count('initRuntime();')==1
	js = js.replace('initRuntime();', 'initRuntime(); runWithFS();')

	assert js.count('var path = NODEFS.realPath(stream.node);') ==1
	js = js.replace('var path = NODEFS.realPath(stream.node);', 'var path = NODEFS.realPath(stream.node);console.log("realPath="+path);')

	## compress inline files ##
	newjs = []
	for ln in js.splitlines():
		if ln.startswith('fileData') and '.push.apply(' in ln:
			a,b = ln.split(', [')
			b = b.replace(' ', '')
			for key in COMPRESSION_MAPPING:
				val = str(COMPRESSION_MAPPING[key])
				if val in b:
					b = b.replace(val, key)
			ln = a + ',[' + b
		newjs.append(ln)

	js = '\n'.join(newjs)

	if wasmgz:
		#assert js.count("function getBinary() {")==1
		#wbin = "Module['wasmBinary']=pako.inflate(atob('%s'));" % base64.b64encode(wasmgz)
		#js = js.replace(
		#	"function getBinary() {",
		#	wbin + "\nfunction getBinary() {"
		#)

		js = js.replace('run();', '/*bypassed run*/;')

		js = js.replace(
			"Module['asm'] = function(global, env, providedBuffer) {",
			"Module['asm'] = function __module_module_do_asm(global, env, providedBuffer, callback) {"
		)

		#r += 'var exports = wasm.instance.exports;'
		#r += "Module['asm'] = exports;"
		#r += "callback(exports);"
		js = js.replace('var exports = createWasm(env);', EMHACK_INIT % base64.b64encode(wasmgz))

		assert js.count(EMHACK)==1
		js = js.replace(EMHACK, EMHACK_NEW)

		js = js.replace('Module["asm"] = asm;', '});')


		js = js.replace("Module['asm'] = asm;", '')


		js = js.replace(
			"Module['preRun'] = [];",
			'/*bypassed preRun=[]*/;'
		)
		js = js.replace("Module['postRun'] = [];", "")
		js = js.replace(
			"var Module = typeof Module !== 'undefined' ? Module : {};",
			"var Module = typeof Module !== 'undefined' ? Module : {preRun:[], postRun:[], canvas:document.getElementById('canvas')};"
		)

		assert js.count("var callback = callbacks.shift();") == 1
		js = js.replace("var callback = callbacks.shift();", "var callback = callbacks.shift();console.log('callRuntimeCallbacks', callback);")


	else:
		js = js.replace(
			'return WebAssembly.instantiate(binary, info);',
			'return WebAssembly.instantiate(pako.inflate(binary),info);'
		)

	return js

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
	open('./tinypy/interpreter_codes.gen.h', 'w').write(tp_vm_enums)
	open('./tinypy/interpreter_codes_debug.gen.h', 'w').write(tp_vm_debug_strings)

	encode_py = '%s = range(%s)' %(','.join(codes), len(codes))
	open('./tpython_interpreter_codes_gen.py', 'w').write(encode_py)



BlendotTypesFiles = '''blendot/mutex.cpp blendot/memory.gen.cpp blendot/pool_allocator.cpp blendot/pool_vector.cpp blendot/message_queue.cpp blendot/object.gen.cpp blendot/node_path.cpp blendot/ip_address.cpp blendot/class_db.cpp blendot/resource.cpp blendot/method_bind.cpp blendot/reference.gen.cpp blendot/ref_ptr.cpp blendot/array.gen.cpp blendot/variant_op.cpp blendot/variant.cpp blendot/string_name.cpp blendot/print_string.cpp blendot/core_string_names.cpp blendot/dictionary.cpp blendot/ustring.cpp blendot/math_funcs.cpp blendot/basis.gen.cpp blendot/vector2.gen.cpp blendot/vector3.gen.cpp blendot/quat.gen.cpp blendot/color.gen.cpp blendot/aabb.gen.cpp blendot/transform.gen.cpp blendot/transform_2d.gen.cpp blendot/rect2.gen.cpp blendot/rid.gen.cpp blendot/scene/main/scene_tree.cpp blendot/scene/main/node.cpp blendot/scene/3d/spatial.gen.cpp blendot/scene/scene_string_names.cpp blendot/main_loop.gen.cpp blendot/engine.gen.cpp blendot/scene/resources/material.cpp blendot/scene/resources/mesh.gen.cpp blendot/scene/resources/surface_tool.cpp blendot/face3.gen.cpp blendot/plane.gen.cpp blendot/scene/resources/shape.cpp blendot/quick_hull.cpp blendot/scene/resources/convex_polygon_shape.cpp blendot/scene/resources/concave_polygon_shape.cpp blendot/triangle_mesh.cpp blendot/servers/visual_server.cpp blendot/image.cpp blendot/geometry.gen.cpp blendot/servers/visual/visual_server_raster.cpp blendot/servers/visual/visual_server_globals.cpp blendot/servers/visual/rasterizer.cpp'''

UninextFiles = '' #' '.join( ["uninext/"+file if file.endswith('.cpp') else '' for file in os.listdir('tinypy/uninext')] )

Makefile = '''
## note this Makefile is autogenerated by rebuild.py ##
VMLIB_FILES=tp.gen.cpp dummy-compiler.cpp runtime.gen.cpp <MODULES>

%.o : %.cpp
	<CC> $(CFLAGS) <DEFINES> -std=c++17 <OPTIONS> <SDL_INCLUDE> -I . <EXTRA_INCLUDES> -c -o $@ $<

all: <EXE>

tinypy/tp.o : tinypy/tp.gen.cpp tinypy/tp*.cpp tinypy/tp*.h

<EXE> : $(VMLIB_FILES:%.cpp=tinypy/%.o) tinypy/vmmain.gen.o
	<CC> <EXEOPTS> -o $@ $^ <LIBS>

clean:
	rm -rf <EXE>
	rm -rf tinypy/*.o

'''

MakefileWithRPMalloc = '''
## note this Makefile is autogenerated by rebuild.py ##
RPMALLOC_FILES=rpmalloc.c
VMLIB_FILES=tp.gen.cpp dummy-compiler.cpp runtime.gen.cpp <MODULES>

%.o : %.cpp
	<CC> $(CFLAGS) <DEFINES> -std=c++17 <OPTIONS> <SDL_INCLUDE> -I . <EXTRA_INCLUDES> -c -o $@ $<

%.o : %.c
	<C> -O3 -DENABLE_THREAD_CACHE=0 -I . -c tinypy/rpmalloc.c -o tinypy/rpmalloc.o

all: <EXE>

tinypy/tp.o : tinypy/tp.gen.cpp tinypy/tp*.cpp tinypy/tp*.h

<EXE> : $(RPMALLOC_FILES:%.c=tinypy/%.o) $(VMLIB_FILES:%.cpp=tinypy/%.o) tinypy/vmmain.gen.o
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
	if '--wasm' in sys.argv:
		cmd.append('--wasm')
	if '--aot-pure' in sys.argv:
		cmd.append('--aot-pure')
	if '--sdl-deprecated' in sys.argv:
		cmd.append('--sdl-deprecated')
	if '--blendot' in sys.argv:
		cmd.append('--blendot')
	if '--debug' in sys.argv:
		cmd.append('--debug')
	if '--debug-calls' in sys.argv:
		cmd.append('--debug-calls')
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

def rebuild(stage=None, exe_name='tpython++'):
	os.system('rm -f tinypy/__user_bytecode__.gen.h')
	os.system('rm -f tinypy/__user_pythonic__.gen.h')
	os.system('rm -f tinypy/__user_pythonic__.pyh')
	os.system('rm -f tinypy/*.gcda')
	
	if stage is None or stage < 2:
		os.system('rm -f /tmp/tinypy.json')

	gen_interpreter_codes( randomize='--secure' in sys.argv)

	mode = 'linux'
	exe = exe_name
	exeopts = ''
	extra_inc = ''  # -I ./tinypy/blendot -I ./tinypy/miniunreal -I ./tinypy/miniode
	defs = ''
	mods = ''
	opts = '-Wcast-align'
	libs = '-lm -ldl -lpthread'
	html_template = None

	C  = 'gcc'
	CC = 'c++'
	if '--clang' in sys.argv:
		opts += ' -Wover-aligned'
		CC = 'clang++-6.0'
		C  = 'clang-6.0'
		clang_path = os.path.expanduser('~/clang+llvm-9.0.0-x86_64-linux-gnu-ubuntu-16.04')
		for arg in sys.argv:
			if arg.startswith('--clang-path='):
				clang_path = arg.split('=')[-1]
		if os.path.isdir(clang_path):
			CC = os.path.join(clang_path, 'bin/clang++')
			C = os.path.join(clang_path, 'bin/clang')


	if '--uninext' in sys.argv:
		defs = '-DTPY_UNINEXT'
		mods = UninextFiles
		assert '--blendot' not in sys.argv
		if '--no-blendot' not in sys.argv:
			sys.argv.append('--no-blendot')
		extra_inc += ' -I ./tinypy/uninext '
		if '--wasm' in sys.argv:
			opts += ' -s USE_SDL=2 -s USE_SDL_IMAGE=2 -s USE_SDL_MIXER=2'

	elif '--no-blendot' in sys.argv or '--includeos' in sys.argv or '--html' in sys.argv or '--wasm' in sys.argv:
		defs = ''
		mods = ''
	elif '--miniunreal' in sys.argv or '--unreal' in sys.argv:
		defs = '-DUNREAL_TYPES'
		mods = ''
		extra_inc += ' -I ./tinypy/miniunreal '
	elif '--blendot' in sys.argv:
		defs = '-DBLENDOT_TYPES'
		mods = BlendotTypesFiles
		assert '--uninext' not in sys.argv
		extra_inc += ' -I ./tinypy/blendot '

	if '--rpmalloc' in sys.argv:
		print("WARN: rpmalloc is not fully compatible with SDL and AOT modules")
		defs += ' -DUSE_RPMALLOC '
		mkfile = MakefileWithRPMalloc.replace('<C>', C)
	else:
		mkfile = Makefile

	if '--profile-hashing' in sys.argv:
		defs += ' -DPROFILE_HASHING '

	if '--big-num' in sys.argv:
		defs += ' -DTP_BIG_NUM'

	if '--debug-gc' in sys.argv:
		defs += ' -DDEBUG_GC'

	if '--debug-sizes' in sys.argv:
		defs += ' -DDEBUG_SIZES'

	if '--debug-str' in sys.argv:
		defs += ' -DDEBUG_STR'
		
	if '--super-tiny' in sys.argv:
		defs += ' -DSUPER_TINY'
	

	aot_modules = False
	sdl_inc = ''
	use_sdl = False

	if '--no-aot-modules' in sys.argv:
		print('NO AOT MODULES')
	else:
		#use_sdl = True
		if '--ode' in sys.argv:
			extra_inc += ' -I ./tinypy/miniode '

			aot_modules = True
			if '--clang' in sys.argv or '--html' in sys.argv or '--wasm' in sys.argv:
				print("WARN: miniode is not yet fully supported by clang")
				print("https://bitbucket.org/odedevs/ode/issues/66/different-behavior-with-clang-vs-gcc")
			elif '--aot' not in sys.argv:
				print("WARN: miniode is not yet fully supported by GCC when compiled without AOT")
				print("body.getRotation() is known to return invalid values")
				print("the workaround is to rebuild with --aot, and make your script fully AOT compatible")
			for odefile in os.listdir('./tinypy/miniode/ode'):
				if odefile.endswith('.cpp'):
					if odefile=='fastdot.cpp':
						pass
					elif odefile.startswith('fast') or odefile in ('resource_control.cpp', 'collision_libccd.cpp'):
						print('skipping: ', odefile)
						continue
					mods += ' miniode/ode/' + odefile
			for odefile in os.listdir('./tinypy/miniode/ode/joints'):
				if odefile.endswith('.cpp'):
					mods += ' miniode/ode/joints/' + odefile
			defs += ' -DUSE_ODE -DODE_PLATFORM_LINUX -DdTHREADING_INTF_DISABLED'
		if '--aot-pure' in sys.argv:
			defs += ' -DPURE_AOT'
		#else:
		#	defs += ' -DUSE_USER_CUSTOM_CPP'

	script = None
	embed_bytecode = False
	miniunreal = False
	unreal_plugin = None
	unreal_ver = None
	unreal_project = os.path.expanduser('~/Documents/Unreal Projects/TPythonPluginTest')
	
	print(sys.argv)
	for arg in sys.argv[1:]:
		if arg.startswith('--html-template='):
			html_template = open( os.path.expanduser(arg.split('=')[-1]), 'rb').read().decode('utf-8')

		elif arg.endswith( ('.unreal', '.unreal/') ):
			unreal_plugin = arg
			#mode = 'unreal'
			if '-DBLENDOT_TYPES' in defs:
				defs = defs.replace('-DBLENDOT_TYPES', '')
				mods = ''
			#if not aot_modules:
			#	defs += ' -DUSE_USER_CUSTOM_CPP'
		elif os.path.isdir(arg):
			unreal_project = arg
		elif arg.startswith('--unreal-'):
			if arg.startswith('--unreal-version='):
				unreal_ver = arg
		elif arg in ('--unreal', '--miniunreal'):
			miniunreal = True
			defs += ' -DMINIUNREAL'

	
	for arg in sys.argv[1:]:
		if arg.endswith( '.py' ):
			script = open(arg).read()
			if 'import sdl' in script:
				use_sdl = True
				aot_modules = True
			cmd = [
				'./tpython++compiler.py', 
				'--beta', 
				'--gen-header=embedded_bytecode.gen.h', 
				arg
			]
			if '--debug' in sys.argv:
				cmd.append('--debug')
			if '--aot' in sys.argv:
				cmd.append('--aot-all')
				if '--aot-pure' in sys.argv:
					cmd.append('--aot-pure')
				if '--wasm' in sys.argv or '--html' in sys.argv:
					if '--server' in sys.argv:
						pass
					else:
						exe = os.path.split(arg)[-1]
			if '--wasm' in sys.argv or '--html' in sys.argv:
				cmd.append('--wasm')
			if '--sdl-deprecated' in sys.argv:
				cmd.append('--sdl-deprecated')
				
			for a in sys.argv:
				if a.startswith('--import-path='):
					cmd.append(a)

			subprocess.check_call(cmd)
			if os.path.isfile('/tmp/embedded_bytecode.gen.h'):
				os.system('cp -v /tmp/embedded_bytecode.gen.h ./tinypy/__user_bytecode__.gen.h')
				embed_bytecode = True
				defs += ' -DUSE_EMBEDDED_BYTECODE'

			else:
				## no bytecode ##
				#open('./tinypy/__user_bytecode__.gen.h', 'wb').write('')
				pass

			if not aot_modules:
				if os.path.isfile('./tinypy/__user_pythonic__.pyh'):
					defs += ' -DUSE_USER_CUSTOM_CPP'
			break

	if '--shared' in sys.argv or unreal_plugin:
		if '--windows' in sys.argv or '--mingw' in sys.argv:
			exe = 'libtpython++.dll'
		else:
			exe = 'libtpython++.so'
		exeopts = '-shared -fPIC '
		opts = '-fPIC '
		defs += ' -DSHAREDLIB'


	gen_interpreter(stage=stage)


	if '--cpython' in sys.argv:
		defs += ' -DUSE_PYTHON'
		libs += ' -lpython3.7m'
		opts += ' -I/usr/include/python3.7m'
		tpyc_gen_h = [
			'static std::string __tpc_source__ = std::string(R"RAWSTRING(',
			open('tpc').read(),
			'',  ## ensure EOL, otherwise CPython will fail to compile this string
			')RAWSTRING");'
		]
		open('./tinypy/tpc.gen.h', 'wb').write('\n'.join(tpyc_gen_h))

	##############################################
	if '--includeos' in sys.argv:
		mode = 'includeos'
		if not os.path.isdir('./tpythonos_build'):
			os.mkdir('tpythonos_build')
			subprocess.check_call(['conan', 'install', '../tinypy', '-pr', 'clang-6.0-linux-x86_64'], cwd='./tpythonos_build')
	elif '--wasm' in sys.argv or '--html' in sys.argv:
		if not os.path.isdir( os.path.expanduser('~/emsdk')):
			install_emsdk()
		mode = 'wasm'
		CC = shutil.which('em++') #os.path.expanduser('~/emsdk/upstream/emscripten/em++')
		libs = ''
		#opts += ' -O3 -fno-rtti -s FILESYSTEM=0 -s DISABLE_EXCEPTION_CATCHING=0'
		## note: blendot types require rtti (run time type info)
		opts += ' -Os '
		exeopts += ''' -s EXPORTED_RUNTIME_METHODS='["ccall", "cwrap", "intArrayFromString", "intArrayToString", "setValue", "getValue", "allocate", "getMemory", "AsciiToString", "stringToAscii", "UTF8ArrayToString", "UTF8ToString"]' '''
		if '--filesystem' in sys.argv or '--uninext' in sys.argv:
			pass
		else:
			exeopts += ' -s FILESYSTEM=0'
		if '--wasmjs' in sys.argv:
			exeopts += ' -s WASM=0'

		if '--uninext' in sys.argv:
			exeopts += ' --embed-file tinypy/uninext/files'

		if '--debug' in sys.argv:
			#exeopts += ' -s DISABLE_EXCEPTION_CATCHING=2 -s FILESYSTEM=0'  ## something requires fs
			#exeopts += ' -s DISABLE_EXCEPTION_CATCHING=2 -s SAFE_HEAP=1 -s WARN_UNALIGNED=1'  ## no need for SAFE_HEAP with wasm, because it can do unaligned casts?
			exeopts += ' -s DISABLE_EXCEPTION_CATCHING=2 -s WARN_UNALIGNED=1'
		else:
			#exeopts += ' -s WARN_UNALIGNED=1 -s ALLOW_MEMORY_GROWTH=1'  ## allowing memory growth will freeze on startup with SDL
			#exeopts += ' -s WARN_UNALIGNED=1 -s ASYNCIFY' ## asyncify is deprecated, and makes the binary 50% larger anyways
			exeopts += ' -s WARN_UNALIGNED=1'			
			if '--super-tiny' in sys.argv:
				exeopts += ' -s ERROR_ON_UNDEFINED_SYMBOLS=0'

		if '--closure' in sys.argv:
			exeopts += ' --closure 1'

		if '--sdl' in sys.argv or use_sdl:  ## this is also required just at the linker stage
			## SDL1 is better
			#exeopts += ' -s USE_SDL=2'
			#if '--sdl-image' in sys.argv:

			## note: png requires zlib
			#exeopts += """ -s USE_SDL_IMAGE=2 -s SDL2_IMAGE_FORMATS='["png"]' -s USE_SDL_MIXER=2"""
			exeopts += """ -s USE_SDL_IMAGE=2 -s SDL2_IMAGE_FORMATS='["gif"]' -s USE_SDL_MIXER=2 -s TOTAL_MEMORY=512MB"""
			pass
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
		if '--shared' not in sys.argv and not unreal_plugin:
			exe += '.exe'
		mode = 'windows'
		opts += ' -Os -finline-small-functions'
		exeopts += ' -Os'

	elif '--android' in sys.argv:
		print('ensure that you have installed android sdk28 and build-tools28')
		print('sudo ./sdkmanager  "platforms;android-28" "build-tools;28.0.0"')
		mode = 'android'
		if '--sdl' not in sys.argv or not use_sdl:
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
		if '--profile' in sys.argv:
			opts += ' -O3 -g -pg '
			exeopts += ' -O3 -g -pg '
		elif '--clang' in sys.argv:
			opts += ' -Ofast -march=native '
			exeopts += opts

		else:
			if '--secure-binary' in sys.argv:
				opts += ' -O2 -finline-small-functions -march=native'
			else:
				#opts += ' -O3 -funroll-loops -finline-small-functions -march=native -ffast-math -fno-math-errno -funsafe-math-optimizations -fno-signed-zeros -fno-trapping-math -frename-registers'
				opts += ' -O3 -funroll-loops -finline-small-functions -march=native -frename-registers'
				if '--big-num' in sys.argv:
					opts += ' -m128bit-long-double'
					#-m96bit-long-double
					#-m128bit-long-double
					#-mlong-double-64
					#-mlong-double-80
					#-mlong-double-128

			exeopts += opts
		if '--gcc5' in sys.argv:
			CC = '/usr/bin/g++-5'
			assert os.path.isfile(CC)

	###############################
	if '--debug' in sys.argv:
		defs += ' -DDEBUG'
		opts += ' -g -rdynamic'
	elif '--debug-calls' in sys.argv:
		defs += ' -DDEBUG_CALLS'
		opts += ' -g -rdynamic'

	if '--secure-binary' in sys.argv:
		if '-rdynamic' not in opts:
			opts += ' -rdynamic'
		exeopts += ' -fPIC -Wl,--export-dynamic'

	if '--sdl' in sys.argv or use_sdl:
		#mods += ' module_sdl.cpp'  # the entire sdl module is actually just in module_sdl.h
		if '--sdl-deprecated' in sys.argv:
			defs += ' -DUSE_SDL'        # from runtime.cpp, module_sdl.h will be included  DEPRECATED, replaced by module_sdl.aot.pyh
		if mode == 'wasm':
			#exeopts += """ -s USE_SDL=2 -s USE_SDL_IMAGE=2 -s SDL2_IMAGE_FORMATS='["png"]' -s TOTAL_MEMORY=33554432"""
			exeopts += ' -s USE_SDL=2'
			#if '--sdl-image' in sys.argv:
			#	exeopts += """ -s USE_SDL_IMAGE=2 -s SDL2_IMAGE_FORMATS='["png"]'"""
			if '--allow-memory-growth' in sys.argv:
				exeopts += ' -s ALLOW_MEMORY_GROWTH=1'
		else:
			sdl_inc = '-I/usr/include/SDL2'
			#libs += ' -lSDL2'
			libs += ' -lSDL2 -lSDL2_mixer -lSDL2_image'

	if unreal_plugin:
		if not os.path.isdir(unreal_project):
			os.makedirs( unreal_project )
		if not os.path.isdir( os.path.join(unreal_project, 'Plugins/3rdparty') ):
			os.makedirs( os.path.join(unreal_project, 'Plugins/3rdparty') )
		cmd = [
			'./tpython++compiler.py', 
			'--beta', 
			'--unreal'
		]
		if mode=='windows':
			cmd.append('--windows')
		if unreal_ver:
			cmd.append(unreal_ver)
		cmd.extend([
			unreal_plugin,
			unreal_project,
		])
		subprocess.check_call(cmd)

	if mode == 'includeos':
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
		if '--clang' in sys.argv:
			os.system('rm *.profraw')
			makefile_gen_pgo = mkfile.replace("<CC>", CC).replace('<DEFINES>', defs).replace('<LIBS>', libs).replace('<EXE>', exe).replace('<EXEOPTS>', ' -fprofile-instr-generate=default.profraw ' + exeopts).replace('<OPTIONS>', ' -fprofile-generate ' + opts).replace('<MODULES>', mods).replace('<SDL_INCLUDE>', sdl_inc)
			makefile_use_pgo = mkfile.replace("<CC>", CC).replace('<DEFINES>', defs).replace('<LIBS>', libs).replace('<EXE>', exe).replace('<EXEOPTS>', ' -fprofile-instr-use ' + exeopts).replace('<OPTIONS>', ' -fprofile-use ' + opts).replace('<MODULES>', mods).replace('<SDL_INCLUDE>', sdl_inc)
		else:
			makefile_gen_pgo = mkfile.replace("<CC>", CC).replace('<DEFINES>', defs).replace('<LIBS>', libs).replace('<EXE>', exe).replace('<EXEOPTS>', ' -fprofile-generate ' + exeopts).replace('<OPTIONS>', ' -fprofile-generate ' + opts).replace('<MODULES>', mods).replace('<SDL_INCLUDE>', sdl_inc)
			makefile_use_pgo = mkfile.replace("<CC>", CC).replace('<DEFINES>', defs).replace('<LIBS>', libs).replace('<EXE>', exe).replace('<EXEOPTS>', ' -fprofile-use ' + exeopts).replace('<OPTIONS>', ' -fprofile-use ' + opts).replace('<MODULES>', mods).replace('<SDL_INCLUDE>', sdl_inc)

		open('Makefile', 'wb').write(makefile_gen_pgo)
		subprocess.check_call(['make', 'clean'])
		subprocess.check_call(['make'])
		subprocess.check_call(['time', './tpython++'])

		if '--clang' in sys.argv:
			for f in os.listdir('.'):
				if f.endswith('.profraw'):
					subprocess.check_call(['llvm-profdata-6.0', 'merge', '-output=default.profdata', f])
					break

		open('Makefile', 'wb').write(makefile_use_pgo)
		subprocess.check_call(['make', 'clean'])
		subprocess.check_call(['make'])
		subprocess.check_call(['time', './tpython++'])

	else:
		makefile = mkfile.replace("<CC>", CC).replace('<DEFINES>', defs).replace('<LIBS>', libs).replace('<EXE>', exe).replace('<EXEOPTS>', exeopts).replace('<OPTIONS>', opts).replace('<MODULES>', mods).replace('<SDL_INCLUDE>', sdl_inc).replace('<EXTRA_INCLUDES>', extra_inc)
		if mode=='windows':
			makefile = makefile.replace('-rdynamic', '')

		open('Makefile', 'w').write(makefile)
		print(makefile)
		subprocess.check_call(['make', 'clean'])
		subprocess.check_call(['make'])
		if unreal_plugin:
			if mode=='windows':
				subprocess.check_call(['cp', '-v', './libtpython++.dll', os.path.join(unreal_project, 'Plugins/3rdparty')])
			else:
				subprocess.check_call(['cp', '-v', './libtpython++.so', os.path.join(unreal_project, 'Plugins/3rdparty')])

		if '--profile' in sys.argv:
			subprocess.check_call(['./tpython++'])
			subprocess.check_call(['gprof','-p','-b', 'tpython++', 'gmon.out'])

	########### post build processing ###########

	if mode == 'wasm':
		pakopath = os.path.expanduser('~/pako/dist/pako_inflate.min.js')
		pako = ''
		is_html = False
		if exe.endswith('.html'):
			exe = exe.split('.html')[0]
			is_html = True

		## insert user source code into html file ##
		if script and is_html:
			if not html_template:
				html = open('./%s.html' %exe, 'rb').read().decode('utf-8')
				assert '</body>' in html
				script = script.replace("<", "&lt;").replace(">", "&gt;")
				if os.path.isfile('./tinypy/__user_pythonic__.gen.h'):
					cpp = open('./tinypy/__user_pythonic__.gen.h', 'rb').read().decode('utf-8')
					if 'tp_obj sdl=sdlwrapper_new();' in cpp:
						cpp = cpp.split('tp_obj sdl=sdlwrapper_new();')[-1]
					js = ''
					if os.path.isfile('/tmp/__tpython_js_debug__.js'):
						js = open('/tmp/__tpython_js_debug__.js', 'rb').read().decode('utf-8')
					py = ''
					if os.path.isfile('/tmp/__tpython_py_debug__.py'):
						py = open('/tmp/__tpython_py_debug__.py', 'rb').read().decode('utf-8')
					cpp = cpp.replace("<", "&lt;").replace(">", "&gt;")
					js  = js.replace("<", "&lt;").replace(">", "&gt;")
					py  = py.replace("<", "&lt;").replace(">", "&gt;")
					html = html.replace('</body>', SIMPLE_JS_EDITOR + '<hr/><pre style="background-color:black;color:green" contenteditable="true" id="TPY_SRC">%s</pre><hr/><pre>%s</pre><hr/><pre>%s</pre><hr/><pre>%s</pre></body>' %(script, js, py, cpp))
				else:
					html = html.replace('</body>', SIMPLE_JS_EDITOR + '<hr/><pre contenteditable="true" id="TPY_SRC">%s</pre></body>' %script)

			if '--keyboard-events' in sys.argv:
				pass
			else:
				js = open('./%s.js' %exe, 'rb').read().decode('utf-8')
				#assert "var Module = typeof Module !== 'undefined' ? Module : {};" in js
				js = js.replace(
					"var Module = typeof Module !== 'undefined' ? Module : {};",
					"var Module = typeof Module !== 'undefined' ? Module : {};\nModule['doNotCaptureKeyboard']=true;"
			
				)
				open('./%s.js' %exe, 'wb').write( js.encode('utf-8') )

		elif exe.endswith('.js'):
			exe = exe.split('.js')[0]


		wasmgz = None
		if os.path.isfile(pakopath):
			pako = open(pakopath).read()
			subprocess.check_call(['gzip', '--force', './%s.wasm' %exe])
			wasmgz = open('./%s.wasm.gz' %exe, 'rb').read()
		else:
			print(PAKO_MISSING)

		c = js
		if os.path.isfile('/tmp/tpython_preload_libs.js'):
			a = open('/tmp/tpython_preload_libs.js').read()
			b = open('./%s.js' %exe).read()
			if pako and '--no-pako-lib' not in sys.argv:
				c = pako + '\n' + a + '\n' + pakoify(b, exe=exe, wasmgz=wasmgz)
			else:
				c = a + '\n' + b
			open('./%s.js' %exe, 'wb').write(c.encode('utf-8'))
		elif pako:
			b = open('./%s.js' %exe ).read()
			if '--no-pako-lib' in sys.argv:
				c = pakoify(b, exe=exe, wasmgz=wasmgz)
			else:
				c = pako + '\n' + pakoify(b, exe=exe, wasmgz=wasmgz)
			open('./%s.js' %exe, 'wb').write(c.encode('utf-8'))

		if html_template:
			if '--external-js' in sys.argv:
				assert '</head>' in html_template
				html = html_template.replace('</head>', '<script async type="text/javascript" src="tpython%2B%2B.js"></script></head>')
			else:
				assert '</body>' in html_template
				html = html_template.replace('</body>', '<script type="text/javascript">%s</script></body>' % c)

		open('./%s.html' %exe, 'wb').write( html.encode('utf-8') )

			
	#####################
	if mode == 'windows':
		for dll in ['libstdc++-6.dll','libgcc_s_seh-1.dll', 'libwinpthread-1.dll']:
			if not os.path.isfile(dll):
				if dll == 'libwinpthread-1.dll':
					os.system('cp -v /usr/x86_64-w64-mingw32/lib/%s ./%s' %(dll, dll))
				else:
					os.system('cp -v /usr/lib/gcc/x86_64-w64-mingw32/5.3-posix/%s ./%s' %(dll, dll))
			if unreal_plugin:
				subprocess.check_call(['cp', '-v', dll, os.path.join(unreal_project, 'Plugins/3rdparty')])


def main():
	if os.path.isfile('/tmp/tpython_preload_libs.js'):
		os.system('rm -f /tmp/tpython_preload_libs.js')
	if os.path.isfile('/tmp/__tpython_js_debug__.js'):
		os.system('rm -f /tmp/__tpython_js_debug__.js')
	if os.path.isfile('/tmp/__tpython_py_debug__.py'):
		os.system('rm -f /tmp/__tpython_py_debug__.py')

	#if '--clean' in sys.argv or '--html' in sys.argv or '--wasm' in sys.argv:
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
		os.system('rm -f tinypy/miniode/ode/*.o')
		os.system('rm -f tinypy/miniode/ode/joints/*.o')
		os.system('rm -f /tmp/embedded_bytecode.gen.h')


	trans_files = []
	vis_args = []
	for arg in sys.argv:
		if arg.endswith( ('.pyc++', '.pyh') ):
			trans_files.append(arg)
		elif arg.startswith('--vis'):
			vis_args.append(arg)

	if len(trans_files):
		for arg in trans_files:
			cmd = [
				'./tpython++compiler.py', 
				arg
			]
			if '--debug' in sys.argv:
				cmd.append('--debug')
			if vis_args:
				cmd.extend(vis_args)
			if '--wasm' in sys.argv:
				cmd.append('--wasm')
			print(cmd)
			subprocess.check_call(cmd)

	elif '--secure-binary' in sys.argv:
		rebuild(stage=1)
		rebuild(stage=2)
	else:
		rebuild()

main()
