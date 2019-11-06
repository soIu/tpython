#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, sys, subprocess, random, json

def bin_scramble(fname, finfo, mangle_map):
	scram = finfo['scramble']
	ok = False
	for mangled in mangle_map:
		if scram in mangled:
			scram = mangled
			ok = True
	if not ok:
		print('WARN: can not find mangled version of: ' + scram)
		return scram

	xorkey = []
	xscram = []
	for i in range(len(scram)):
		x = int( random.uniform(1,255) )
		xorkey.append(x)
		c = ord(scram[i]) ^ x
		xscram.append( c )

	lambda_scram = [
		'char _[%s];' %len(scram),
		'int __[%s]{%s};' %(len(scram), str(xscram)[1:-1] ),
		'int ___[%s]{%s};' %(len(scram), str(xorkey)[1:-1] ),
		'for (int _i=0; _i<%s; _i++) _[_i]=__[_i]^___[_i];' %len(scram),
		##'std::cout<< std::string(_, %s) <<std::endl;' %len(scram),
		'return std::string(_, %s);' %len(scram)
	]
	lambda_scram = ' '.join(lambda_scram)
	bscram = '( (%s (*)(%s))(dlsym(__libself__,[](){%s}().c_str() )) )' %(finfo['returns'], ','.join(finfo['arg_types']), lambda_scram)
	#bscram = '( (%s (*)(%s))(dlsym(dlopen(NULL, 1),[](){%s}().c_str() )) )' %(finfo['returns'], ','.join(finfo['arg_types']), lambda_scram)
	return bscram

def auto_semicolon(ln):
	s = ln.strip()
	if not s.endswith( ('{', '}', '(', ',', ':') ) and not s.startswith('#'):
		if not s=='else' and not s.startswith( ('if ', 'if(') ):
			if not s.endswith(';') and s:
				if not s.startswith("TP_LOOP("):
					ln += ';'
	return ln

def pythonicpp( source, header='', file_name='', info={}, swap_self_to_this=False, binary_scramble=False, mangle_map=None ):
	if not type(source) is list:
		source = source.splitlines()
	out = []
	if header:
		out.append(header)
	prev = ''
	prevs = ''
	previ = -1
	autobrace = 0
	autofunc = 0
	mods = {}
	modname = None
	in_class = False
	class_indent = 0
	class_name = None
	class_has_init = False
	classes = {}
	nsbrace = -1
	lambdabrace = []
	define = []
	define_ident = -1
	if 'functions' in info:
		functions = info['functions']
	else:
		functions = {}

	for line_num, ln in enumerate(source):
		s = ln.strip()

		## check for function calls, or forward defs
		if not s.startswith('def '):
			for fname in functions:
				if s.count(fname+'(')==1 or s.count(fname+')')==1 or s.count(fname+'}')==1:
					prevchar = ln[ ln.index(fname)-1 ]
					if prevchar in '\t +=-*/[]();,?':
						sig = '%s:%s call: `%s`' %(file_name, fname, s)
						if sig not in functions[fname]['calls']:
							functions[fname]['calls'].append(sig)
						if 'scramble' in functions[fname]:
							finfo = functions[fname]
							scram = finfo['scramble']

							ok = False
							if mangle_map and binary_scramble:
								if fname != '__init_libself__' and not 'static' in finfo and 'auto' not in finfo['arg_types'] and 'std::function<tp_obj(tp_vm*)>' not in finfo['arg_types'] and len(finfo['defs'])==1 and '...' not in finfo['arg_types']:
									for mangled in mangle_map:
										if scram in mangled:
											scram = mangled
											ok = True
									if not ok:
										print('WARN: can not find mangled version of: ' + scram)

							if ok and binary_scramble:

								if '--debug-obfuscate' in sys.argv:
									bscram = '( (%s (*)(%s)) ( [](){std::cout<<__libself__<<std::endl<<"%s"<<std::endl; auto fptr=dlsym(__libself__,"%s"); std::cout<<fptr<<std::endl; return fptr;}() ) )' %(finfo['returns'], ','.join(finfo['arg_types']), scram, scram)
								else:
									#bscram = '( (%s (*)(%s))(dlsym(__libself__,"%s")) )' %(finfo['returns'], ','.join(finfo['arg_types']), scram)
									bscram = bin_scramble(fname, finfo, mangle_map)

								ln = ln.replace(fname, bscram)

							else:
								ln = ln.replace(fname, scram)

							s = ln.strip()


		if s.endswith('\\'):
			out.append(ln)
			continue

		indent = 0
		for c in ln:
			if c == '\t':
				indent += 1
			else:
				break

		#if s:
		if not len(define):
			if lambdabrace and indent <= lambdabrace[-1]:
				brace = lambdabrace.pop()
				b = '\t' * brace
				b += '};'
				out.append(b)

			elif indent <= nsbrace:
				b = '\t' * nsbrace
				b += '}  // end of namespace'
				out.append(b)
				nsbrace = 0
			elif indent < previ and autobrace:
				braces = previ - indent
				b = '\t' * indent
				b += '}'*braces
				out.append(b)

			if in_class and indent <= class_indent:
				in_class = False
				class_indent = 0
				assert out[-1][-1] == '}'
				#out.append('	;// end of class: ' + class_name)
				out[-1] += ';	// end of class: ' + class_name
				class_name = None

		if not s:
			in_class = False

		if s.startswith('##'):
			ln = ln.replace('##', '//')
			out.append(ln)

		#elif s.startswith('#'):
		#	out.append(ln)
		#	if ln == '#endif':
		#		autobrace = 0
		#	continue

		elif s.startswith('import '):
			inc = s.split()[-1]
			if inc.startswith("<"):
				assert inc.endswith(">")
			elif not inc.startswith('"'):
				inc = '"' + inc + '"'
			out.append('#include ' + inc)
		elif s.startswith('define('):
			assert s.endswith(')')
			defname = s[len('define(') : s.index('=') ]
			defval  = s[ s.index('=')+1 : -1]
			out.append('#define %s %s' %(defname, defval))
		elif s.startswith('define ') and s.endswith(':'):
			define_ident = indent
			defname = s[len('define ') : -1 ]
			define.append('#define %s \\' %defname)
			continue
		elif len(define):
			if indent <= define_ident:
				assert define[-1].endswith('\\')
				define[-1] = define[-1][:-1]
				out.extend(define)
				define = []
				define_ident = -1
				out.append( auto_semicolon(ln) )
			else:
				define.append(ln + '\\')
		elif s.startswith('undef('):
			assert s.endswith(')')
			defname = s.split('(')[-1].split(')')[0]
			out.append('#undef %s' %defname)

		elif s.startswith('@module'):
			assert s.count('(')==1
			assert s.count(')')==1
			modname = s.split('(')[-1].split(')')[0].strip()
			assert modname
			if modname not in mods:
				mods[modname] = []
			out.append('// module: ' + modname)
		elif s == '@const':
			pass
		elif s == '@static':
			pass

		elif ' def[' in s and ln.endswith(':'):
			ln = ln.replace(' def[', '[')
			ln = ln[:-1]+ '{'
			lambdabrace.append(indent)
			out.append(ln)

		elif s.startswith('namespace ') and s.endswith(':'):
			assert not nsbrace  ## no nested namespace defs
			nsbrace = indent
			out.append( ('\t'*indent) + s[:-1] + '{')
			autobrace = 0
		elif s.startswith('namespace ') and s.endswith('{'):
			out.append( ln )
			autobrace = 0

		elif s.startswith('class') and s.endswith(':'):
			in_class = True
			class_indent = indent
			class_name = s[:-1].split()[-1].strip()
			classes[ class_name ] = {}  ## methods
			out.append( 'class %s: public tp_obj {' %class_name)
			out.append( '	public:')

		elif s.startswith('def '):
			is_forward_decl = False
			if s.endswith(';'):
				is_forward_decl = True
			else:
				if not s.endswith( ':' ):
					raise SyntaxError(ln)
				autobrace += 1
				autofunc += 1

			func_name = s[len('def ') : ].split('(')[0].strip()
			is_scram = False
			unscram_name = None

			if func_name == '__init__':
				assert in_class
				func_name = class_name
			elif not in_class and func_name in functions and 'scramble' in functions[func_name]:
				is_scram = True
				unscram_name = func_name
				func_name = functions[func_name]['scramble']

			if '->' in s:
				returns = s[:-1].split('->')[-1]
			elif in_class and func_name == class_name:
				returns = ''
				class_has_init = True
			elif prevs.startswith('@module') or (in_class and class_has_init):
				returns = 'tp_obj'
			elif 'operator' in func_name:
				returns = ''
			else:
				returns = 'void'

			if prevs.startswith('@module'):
				args = ['TP']
				tpargs = []
			else:
				args = []

			#rawargs = s.split('(')[-1].split(')')[0]
			rawargs = s.split('->')[0][ s.index('(')+1 : s.rindex(')') ]
			arg_types = []
			for i, arg in enumerate(rawargs.split(',')):
				arg = arg.strip()
				if not arg:
					continue

				if in_class:
					if i==0:
						assert arg == 'self'
						if func_name == class_name:
							args.append('TP')
					#elif i==1 and arg=='TP':
					#	args.append(arg)
					else:
						if ' ' in arg:
							args.append(arg)
						else:
							args.append('tp_obj ' +arg)
							if func_name == class_name:
								out.append('		tp_obj %s;' %arg)

				elif prevs.startswith('@module'):
					if arg == 'TP':
						if i != 0:
							raise SyntaxError('ERROR: `TP` is automatically inserted as the first argument for modules')
					else:
						if ' ' in arg:
							atype, aname = arg.split()
							tpargs.append(('\t'*(indent+1))+'auto %s = %s();' %(aname, atype))
						else:
							tpargs.append(('\t'*(indent+1))+'auto %s = TP_OBJ();' %arg)

				else:
					if ' ' not in arg and arg != 'TP' and arg != 'void' and arg != '...':
						arg = 'auto ' + arg
						arg_types.append('auto')
					elif arg == 'TP':
						arg_types.append('tp_vm*')
					elif arg == '...':
						arg_types.append('...')
					else:
						if ' ' in arg:
							atype = arg[ : arg.rindex(' ') ].strip()
							aname = arg.split()[-1]
							pointers = aname.count('*')
							if aname.endswith(']'):
								assert aname.count('[') == aname.count(']')
								pointers += aname.count(']')
							if pointers:
								atype += '*' * pointers
							if atype=='TP':
								arg_types.append('tp_vm*')
							else:
								arg_types.append(atype)

					args.append( arg )



			if not in_class and not is_scram and not is_forward_decl:
				if func_name not in functions:
					functions[ func_name ] = {'defs':[], 'calls':[]}

				functions[ func_name ]['returns'] = returns
				functions[ func_name ]['args'] = args
				functions[ func_name ]['arg_types'] = arg_types
				if prevs == '@static':
					functions[ func_name ]['static'] = True

				sig = '%s:%s `%s`' %(file_name, line_num, s)
				if sig not in functions[func_name]['defs']:
					functions[func_name]['defs'].append(sig)
			elif not in_class and not is_scram and is_forward_decl and func_name=='module_init':  ## special case
				if func_name not in functions:
					functions[ func_name ] = {'defs':[], 'calls':[]}
				functions[ func_name ]['returns'] = returns
				functions[ func_name ]['args'] = args
				functions[ func_name ]['arg_types'] = arg_types
				if prevs == '@static':
					functions[ func_name ]['static'] = True


			exopts = ''
			if prevs == '@const':
				exopts = ' const '
			if prevs == '@static':
				returns = 'static ' + returns

			if in_class:
				func = '\t' * indent
			else:
				func = '\t'

			if is_forward_decl:
				if in_class and func_name == class_name:
					func += '%s(%s) %s;' %(func_name, rawargs, exopts)
				else:
					func += '%s %s(%s) %s;' %(returns, func_name, rawargs, exopts)
			else:
				if in_class and func_name == class_name:
					func += '%s(%s) %s{' %(func_name, ','.join(args), exopts)
				else:
					func += '%s %s(%s) %s{' %(returns, func_name, ','.join(args), exopts)

			out.append(func)

			if prevs.startswith('@module'):
				if is_scram:
					mods[modname].append( {'scram':func_name, 'unscram':unscram_name} )
				else:
					mods[modname].append(func_name)


				out.extend(tpargs)

			if in_class and func_name==class_name:
				out.append('			this->type.type_id = TP_OBJECT;')
				out.append('			this->dict.val = tpd_dict_new(tp);')
				out.append('			this->obj.info->meta = tp_None;')
				## generate lambda wrappers
				for methname in classes[ class_name ]:
					methargs = classes[ class_name ][methname]
					margs =  ','.join( ['TP_OBJ()' for ma in methargs] )
					wrapper = '			std::function<tp_obj(tp_vm*)> __%s_wrapper = [=](tp_vm *tp){return this->%s(%s);};' %(methname, methname, margs)
					out.append(wrapper)
					out.append('			tp_set(tp, *this, tp_string_atom(tp, "%s"), tp_function(tp, __%s_wrapper));' %(methname, methname))
			elif in_class:
				classes[ class_name ][ func_name ] = args

		elif s.startswith('switch ') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			w += 'switch(' + s[len('switch '):-1] + ') {'
			out.append(w)

		elif s.startswith('case ') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			w += 'case ' + s[len('case '):] + '{'
			out.append(w)

		elif s == 'default:':
			autobrace += 1
			out.append(ln + '{')

		elif s.startswith('goto ') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			w += s[len('goto '):] + '{'
			out.append(w)

		elif s.startswith('while ') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			w += 'while(' + s[len('while '):-1] + ') {'
			out.append(w)

		elif s.startswith( ('for ', 'for(','for (') ) and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			loop = s[len('for '):-1]
			if not loop.startswith('('):
				loop = '(' + loop
			if not loop.endswith(')'):
				loop += ')'
			w += 'for ' + loop + ' {'
			out.append(w)

		elif s.startswith('try') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			w += 'try ' + s[len('while '):-1] + ' {'
			out.append(w)

		elif s.startswith('catch ') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			w += 'catch ' + s[len('while '):-1] + ' {'
			out.append(w)

		elif s.startswith('if not ') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			w += 'if(!(' + s[len('if not '):-1] + ')) {'
			out.append(w)

		elif s.startswith('if ') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			w += 'if(' + s[len('if '):-1] + ') {'
			out.append(w)

		elif s.startswith('elif not ') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			w += 'else if(!(' + s[len('elif not '):-1] + ')) {'
			out.append(w)

		elif s.startswith('elif ') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			w += 'else if(' + s[len('elif '):-1] + ') {'
			out.append(w)

		elif s == 'else:':
			autobrace += 1
			w = '\t' * indent
			w += 'else {'
			out.append(w)

		elif s == 'with scope:':
			autobrace += 1
			w = '\t' * indent
			w += '{ // new scope'
			out.append(w)

		else:

			if in_class and swap_self_to_this:
				ln = ln.replace('self.', 'this->')
			ln = auto_semicolon(ln)
			out.append(ln)

		prev = ln
		prevs = s
		previ = indent

	if previ >= 2:
		out.append('}' * (previ-1) )
	#elif autofunc:
	#	out.append('} // autobrace: %s' %previ)

	if mods:
		## generate module_init
		mod_init = 'module_init'
		if functions and 'module_init' in functions:
			if 'scramble' in functions['module_init']:
				mod_init = functions['module_init']['scramble']


		out.append('void %s(TP) {' %mod_init)

		tp_import = 'tp_import'
		tp_string_atom = 'tp_string_atom'
		tp_set = 'tp_set'
		tp_function = 'tp_function'
		if binary_scramble:
			tp_import = bin_scramble('tp_import', functions['tp_import'], mangle_map)
			tp_set = bin_scramble('tp_set', functions['tp_set'], mangle_map)
			tp_function = bin_scramble('tp_function', functions['tp_function'], mangle_map)
		elif functions and 'tp_import' in functions:
			if 'scramble' in functions['tp_import']:
				tp_import = functions['tp_import']['scramble']
			if 'scramble' in functions['tp_set']:
				tp_set = functions['tp_set']['scramble']
			if 'scramble' in functions['tp_function']:
				tp_function = functions['tp_function']['scramble']

		for i,modname in enumerate(mods):
			m = 'mod%s' %i
			out.append('	tp_obj %s = %s(tp, tp_string_atom(tp, "%s"),tp_None, tp_string_atom(tp, "<c++>"));' %(m, tp_import, modname))
			for func in mods[modname]:
				if type(func) is dict:
					scram = func['scram']
					unscram = func['unscram']
					out.append('	%s(tp, %s, tp_string_atom(tp, "%s"), %s(tp, %s));' %(tp_set, m, unscram, tp_function, scram))
				else:
					out.append('	%s(tp, %s, tp_string_atom(tp, "%s"), %s(tp, %s));' %(tp_set, m,func, tp_function, func))
		out.append('}')

	cpp = '\n'.join(out)
	if '--inspect-pythonic++' in sys.argv:
		raise RuntimeError(cpp)

	if 'classes' in info:
		info['classes'].update( classes )

	return cpp

def metapy2tinypypp( source ):
	shared = []
	right_side = []
	thread_local = []
	thread = None
	cpy = None
	cpp = []
	in_cpp = False
	for ln in source.splitlines():
		if u'┃' in ln:
			assert ln.count(u'┃')==1
			a,b = ln.split(u'┃')
			shared.append(a)
			right_side.append(b)
		elif ln.startswith('with c++:'):
			cpp = []
			in_cpp = True
		elif ln.startswith('with python:'):
			cpy = []
		elif ln.startswith('with thread:'):
			thread = []
			thread_local.append(thread)
		elif in_cpp:
			if not ln.strip():
				in_cpp = False
			else:
				cpp.append(ln)
		elif thread is not None:
			if ln.startswith('\t'):
				thread.append( ln[1:] )
			else:
				thread = None
		elif cpy is not None:
			if ln.startswith('\t'):
				cpy.append( ln[1:] )
			else:
				s = '\n'.join(cpy)
				shared.append("python.run('''%s''')" %s)
				cpy = None
		elif len(right_side) and not ln.strip():
			shared.extend( right_side )
			right_side = []
		else:
			shared.append(ln)

	scripts = []
	if len(thread_local):
		for thread_code in thread_local:
			script = '\n'.join(shared)
			script += '\n'
			script += '\n'.join(thread_code)
			scripts.append(script)
	else:
		script = '\n'.join(shared)
		scripts.append(script)

	#cpp = pythonicpp( cpp, swap_self_to_this=True )
	cpp = '\n'.join(cpp)
	return scripts, cpp

def walk_path(path, res):
	for file in os.listdir(path):
		if file.endswith(('.pyc++', '.pyh')):
			res.append([path,file])
		elif os.path.isdir(os.path.join(path,file)):
			walk_path( os.path.join(path,file), res)

def pythonicpp_translate( path, secure=False, secure_binary=False, mangle_map=None, obfuscate_map=None ):
	print(path)
	new_obfuscate = {}
	info = {'classes':{}, 'functions':{}, 'obfuscations':new_obfuscate}
	files = []
	walk_path(path, files)

	if secure:
		## first pass gather function info
		for path, file in files:
			if file.endswith( '.pyc++' ):
				print(file)
				cpp = pythonicpp( open(os.path.join(path,file),'rb').read().decode('utf-8'), header="/*generated from: %s*/" %file, info=info )
			elif file.endswith( '.pyh' ):
				print(file)
				cpp = pythonicpp( open(os.path.join(path,file),'rb').read().decode('utf-8'), header="/*generated from: %s*/" %file, info=info )

		if '--debug' in sys.argv:
			print('classes:')
			for cname in info['classes']:
				print('	' + cname)
			print('functions:')

		alphabet = 'abcdefghijklmnopqrstuvwxyz'
		skip = 'main crash_handler print _tp_min _tp_gcinc tp_default_echo tp_string_len tp_string_getptr tp_string_atom tp_str tp_true len tp_params_v tpd_list_find'.split()
		for fname in info['functions']:

			if '--debug' in sys.argv:
				print('	' + fname)

			if fname not in skip:
				if 'operator' in fname or '::' in fname:
					continue
				if obfuscate_map:
					if fname not in obfuscate_map:
						raise RuntimeError(fname)
					scram = obfuscate_map[fname]
					info['functions'][fname]['scramble'] = ''.join(scram)

				else:
					scram = [random.choice(alphabet) for i in range(16)]
					if '--debug' in sys.argv:
						info['functions'][fname]['scramble'] = ''.join(scram) + '_' + fname.upper()
					else:
						info['functions'][fname]['scramble'] = ''.join(scram)

					new_obfuscate[fname] =info['functions'][fname]['scramble']

	## final pass apply scrambling
	for path, file in files:
		if file.endswith( '.pyc++' ):
			cpp = pythonicpp( open(os.path.join(path,file),'rb').read().decode('utf-8'), header="/*generated from: %s*/" %file, info=info, binary_scramble=secure_binary, mangle_map=mangle_map )
			open(os.path.join(path, file.replace('.pyc++', '.gen.cpp') ),'wb').write(cpp.encode('utf-8'))
		elif file.endswith( '.pyh' ):
			cpp = pythonicpp( open(os.path.join(path,file),'rb').read().decode('utf-8'), header="/*generated from: %s*/" %file, info=info, binary_scramble=secure_binary, mangle_map=mangle_map )
			open(os.path.join(path, file.replace('.pyh', '.gen.h') ),'wb').write(cpp.encode('utf-8'))

	return info

def main():
	input_file = None
	exargs = []
	pythonicpp_paths = []
	mangle_map = []
	obfuscate_map = {}

	for arg in sys.argv[1:]:
		if arg.endswith('.py'):
			input_file = arg
		elif arg.startswith('--'):
			exargs.append(arg)
		elif os.path.isdir(arg):
			pythonicpp_paths.append( arg )
		elif arg.startswith('[') and arg.endswith(']'):
			mangle_map = json.loads(arg)
		elif arg.endswith('.json'):
			obfuscate_map = json.loads(open(arg,'rb').read())

	if input_file:
		path, name = os.path.split(input_file)

		scripts, cpp = metapy2tinypypp( open(input_file, 'rb').read().decode('utf-8') )

		if cpp:
			open('./tinypy/__user_pythonic__.pyh', 'wb').write(cpp.encode('utf-8'))

		if len(scripts) == 1:
			source = scripts[0]
			tempf = '/tmp/%s_main.py'%name
			open(tempf, 'wb').write(source.encode('utf-8'))
			subprocess.check_call(['./tpc']+exargs+['-o', './%s.bytecode'%name, tempf])
		else:
			for i in range(len(scripts)):
				source = scripts[i]
				tempf = '/tmp/%s_thread%s.py'%(name,i)
				open(tempf, 'wb').write(source.encode('utf-8'))
				subprocess.check_call(['./tpc']+exargs+['-o', './%s_thread%s.bytecode'%(name,i), tempf])

	if pythonicpp_paths:
		for path in pythonicpp_paths:
			print('translate path: ', path)
			info = pythonicpp_translate(
				path, 
				secure='--secure' in sys.argv, 
				secure_binary='--secure-binary' in sys.argv, 
				mangle_map=mangle_map,
				obfuscate_map=obfuscate_map
			)
			if not obfuscate_map:
				p = path.split('/')[-1]
				open('/tmp/%s.json' %p, 'wb').write( json.dumps(info['obfuscations']).encode('utf-8') )

main()

