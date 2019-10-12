#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys, subprocess

def pythonicpp( source ):
	out = []
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
	classes = {}
	for ln in source:
		indent = 0
		for c in ln:
			if c == '\t':
				indent += 1
			else:
				break

		if indent < previ and autobrace:
			braces = previ - indent
			b = '\t' * indent
			b += '}'*braces
			out.append(b)

		if in_class and indent <= class_indent:
			in_class = False
			class_indent = 0
			out.append('	;// end of class: ' + class_name)
			class_name = None

		s = ln.strip()


		if s.startswith('@'):
			assert s.startswith('@module')
			assert s.count('(')==1
			assert s.count(')')==1
			modname = s.split('(')[-1].split(')')[0].strip()
			assert modname
			if modname not in mods:
				mods[modname] = []
			out.append('// module: ' + modname)
		elif s.startswith('class') and s.endswith(':'):
			in_class = True
			class_indent = indent
			class_name = s[:-1].split()[-1]
			classes[ class_name ] = {}  ## methods
			out.append( 'class %s: public tp_obj {' %class_name)
			out.append( '	public:')

		elif s.startswith('def '):
			assert s.endswith(':')
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
			elif prevs.startswith('@module') or in_class:
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
							out.append('		tp_obj %s;' %arg)
							args.append('tp_obj ' +arg)

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
					if ' ' not in arg:
						arg = 'auto ' + arg
					args.append( arg )
			if in_class:
				func = '\t' * indent
			else:
				func = '\t'
			func += '%s %s(%s) {' %(returns, func_name, ','.join(args))
			out.append(func)

			if prevs.startswith('@module'):
				mods[modname].append(func_name)
				out.extend(tpargs)

			if in_class and func_name==class_name:
				out.append('this->type.type_id = TP_OBJECT;')
				out.append('this->dict.val = tpd_dict_new(tp);')
				out.append('this->obj.info->meta = tp_None;')
				## generate lambda wrappers
				for methname in classes[ class_name ]:
					methargs = classes[ class_name ][methname]
					margs =  ','.join( ['TP_OBJ()' for ma in methargs] )
					wrapper = 'std::function<tp_obj(tp_vm*)> __%s_wrapper = [=](tp_vm *tp){return this->%s(%s);};' %(methname, methname, margs)
					out.append(wrapper)
					out.append('tp_set(tp, *this, tp_string_atom(tp, "%s"), tp_function(tp, __%s_wrapper));' %(methname, methname))
			elif in_class:
				classes[ class_name ][ func_name ] = args


		elif s.startswith('while ') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			w += 'while(' + s[len('while '):-1] + ') {'
			out.append(w)

		elif s.startswith('if ') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			w += 'if(' + s[len('if '):-1] + ') {'
			out.append(w)

		elif s == 'else:':
			autobrace += 1
			w = '\t' * indent
			w += 'else {'
			out.append(w)
		else:
			if in_class:
				ln = ln.replace('self.', 'this->')
			if not s.endswith( ('{', '}', '(', ',') ) and not s.startswith('#'):
				if not s=='else' and not s.startswith( ('if ', 'if(') ):
					if not s.endswith(';'):
						ln += ';'
			out.append(ln)

		prev = ln
		prevs = s
		previ = indent

	if autofunc:
		out.append('}')

	if mods:
		## generate module_init
		out.append('void module_init(TP) {')
		for i,modname in enumerate(mods):
			m = 'mod%s' %i
			out.append('tp_obj %s = tp_import(tp, tp_string_atom(tp, "%s"),tp_None, tp_string_atom(tp, "<c++>"));' %(m,modname))
			for func in mods[modname]:
				out.append('tp_set(tp, %s, tp_string_atom(tp, "%s"), tp_function(tp, %s));' %(m,func,func))
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

def main():
	input_file = None
	exargs = []
	for arg in sys.argv[1:]:
		if arg.endswith('.py'):
			input_file = arg
		elif arg.startswith('--'):
			exargs.append(arg)
	assert input_file
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

main()

