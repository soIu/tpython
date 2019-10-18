#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys, subprocess

def pythonicpp( source, header='' ):
	if not type(source) is list:
		source = source.splitlines()
	out = []
	if header:
		out.append(header)
	prev = None
	prevs = None
	previ = None
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

	for ln in source:
		s = ln.strip()
		#if s.startswith('##'):
		#	pass

		indent = 0
		for c in ln:
			if c == '\t':
				indent += 1
			else:
				break

		#if s:
		if True:
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
		#else:
		#	autobrace = 0

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
		elif ln.startswith('	define('):
			assert s.endswith(')')
			defname = s[len('define(') : s.index('=') ]
			defval  = s[ s.index('=')+1 : -1]
			out.append('	#define %s %s' %(defname, defval))
		elif ln.startswith('	undef('):
			assert s.endswith(')')
			defname = s.split('(')[-1].split(')')[0]
			out.append('	#undef %s' %defname)

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
			if not s.endswith(':'):
				raise SyntaxError(ln)
			autobrace += 1
			autofunc += 1
			func_name = s[len('def ') : ].split('(')[0].strip()
			if func_name == '__init__':
				assert in_class
				func_name = class_name

			if '->' in s:
				returns = s[:-1].split('->')[-1]
			elif in_class and func_name == class_name:
				returns = ''
				class_has_init = True
			elif prevs.startswith('@module') or (in_class and class_has_init):
				returns = 'tp_obj'
			else:
				returns = 'void'

			if prevs.startswith('@module'):
				args = ['TP']
				tpargs = []
			else:
				args = []

			rawargs = s.split('(')[-1].split(')')[0]
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
					if ' ' not in arg and arg != 'TP' and arg != 'void':
						arg = 'auto ' + arg
					args.append( arg )
			if in_class:
				func = '\t' * indent
			else:
				func = '\t'

			exopts = ''
			if prevs == '@const':
				exopts = ' const '

			if in_class and func_name == class_name:
				func += '%s(%s) %s{' %(func_name, ','.join(args), exopts)
			else:
				func += '%s %s(%s) %s{' %(returns, func_name, ','.join(args), exopts)
			out.append(func)

			if prevs.startswith('@module'):
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
		else:
			if in_class:
				ln = ln.replace('self.', 'this->')
			if not s.endswith( ('{', '}', '(', ',', ':') ) and not s.startswith('#'):
				if not s=='else' and not s.startswith( ('if ', 'if(') ):
					if not s.endswith(';') and s:
						ln += ';'
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
		out.append('void module_init(TP) {')
		for i,modname in enumerate(mods):
			m = 'mod%s' %i
			out.append('	tp_obj %s = tp_import(tp, tp_string_atom(tp, "%s"),tp_None, tp_string_atom(tp, "<c++>"));' %(m,modname))
			for func in mods[modname]:
				out.append('	tp_set(tp, %s, tp_string_atom(tp, "%s"), tp_function(tp, %s));' %(m,func,func))
		out.append('}')

	cpp = '\n'.join(out)
	if '--inspect-pythonic++' in sys.argv:
		raise RuntimeError(cpp)
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

	cpp = pythonicpp( cpp )
	return scripts, cpp

def pythonicpp_translate( path ):
	for file in os.listdir( path ):
		if file.endswith( '.pyc++' ):
			cpp = pythonicpp( open(os.path.join(path,file),'rb').read(), header="/*generated from: %s*/" %file )
			open(os.path.join(path, file.replace('.pyc++', '.gen.cpp') ),'wb').write(cpp)
		elif file.endswith( '.pyh' ):
			cpp = pythonicpp( open(os.path.join(path,file),'rb').read(), header="/*generated from: %s*/" %file )
			open(os.path.join(path, file.replace('.pyh', '.gen.h') ),'wb').write(cpp)


def main():
	input_file = None
	exargs = []
	pythonicpp_paths = []
	for arg in sys.argv[1:]:
		if arg.endswith('.py'):
			input_file = arg
		elif arg.startswith('--'):
			exargs.append(arg)
		elif os.path.isdir(arg):
			pythonicpp_paths.append( arg )

	if input_file:
		path, name = os.path.split(input_file)

		scripts, cpp = metapy2tinypypp( open(input_file, 'rb').read().decode('utf-8') )

		if cpp:
			open('./tinypy/__user__.gen.h', 'wb').write(cpp.encode('utf-8'))

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
			pythonicpp_translate( path )

main()

