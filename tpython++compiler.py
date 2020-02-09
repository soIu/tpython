#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os, sys, subprocess, random, json
from xml.sax.saxutils import escape
import unrealgen, ast

THREEJS_MISSING = '''

ERROR: because you used `import THREE` in your script the three.js source code is required.
Could not find the three.js source folder in your home directory,
try running the commands below, and then rebuild.

	cd
	git clone https://github.com/mrdoob/three.js.git

'''

UNREAL_VER = '4.24.1'   ## first tested with 4.2.0, current version is 4.23.1

UIFACE_TEMPLATE = '''
#pragma('once')
#include "ModuleManager.h"

class I%s : public IModuleInterface {
	public:
		static I%s& Get() {
			return FModuleManager::LoadModuleChecked<I%s>(FName("%s"));
		}
		static bool IsAvailable(){
			return FModuleManager::Get().IsModuleLoaded(FName("%s"));
		}
};
'''

UPLUGIN_TEMPLATE = '''
{
	"FileVersion" : 3,
	"FriendlyName" : "%s",
	"Version" : 1,
	"VersionName" : "1.0",
	"CreatedBy" : "%s",
	"CreatedByURL" : "%s",
	"EngineVersion" : "%s",
	"Description" : "%s",
	"Category" : "%s",
	"EnabledByDefault" : %s,
	"Modules" :
	[
		{
			"Name" : "%s",
			"Type" : "%s",
			"LoadingPhase" : "%s"
		}
	]
}
'''

UNREAL_BUILD_TEMPLATE = '''
using UnrealBuildTool.Rules;
using System.IO;
 
public class %s : ModuleRules {
	public %s(ReadOnlyTargetRules Target) : base(Target) {
		PrivateIncludePaths.AddRange(new string[] { "%s/Private" });
		PublicIncludePaths.AddRange(new string[] { "%s/Public" });
		PublicDependencyModuleNames.AddRange(new string[] {"%s"});
		var base_path = Path.GetFullPath(
			Path.Combine(
				Path.GetDirectoryName(ModuleDirectory), "../../../3rdparty")
		);
		if (!Directory.Exists(base_path)) {
			Log.TraceError("can not find 3rdparty build folder");
			Log.TraceError(base_path);
		}
		PublicIncludePaths.Add( base_path );
		PublicIncludePaths.AddRange( new string[] {"%s"} );
		var path = Path.Combine(base_path, "libtpython++.so");
		PublicAdditionalLibraries.Add(path);
		PublicAdditionalLibraries.AddRange( new string[] {"%s"});
		PublicDependencyModuleNames.AddRange(
			new string[] {
				"Engine", "Core"
				//"CoreUObject", "Engine", "InputCore", "RHI",
				//"RenderCore", "HTTP", "UMG", "Slate", "SlateCore",
				//"ImageWrapper", "PhysX", "HeadMountedDisplay", "AIModule"
			});
	}
}
'''


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
				if not s.startswith( ("TP_LOOP(", "GENERATED_UCLASS_BODY") ):
					ln += ';'
	return ln

def is_untyped_global_var(s):
	if s.startswith('//'):
		return False
	elif s.startswith('define'):
		return False
	elif s.startswith('('):
		return False
	elif s.count('=') == 1:
		decl, value = s.split('=')
		decl = decl.strip()
		value = value.strip()
		if ' ' not in decl:
			return True
	return False

__guesses = {}

def guess_type_of_var(s, classes=None, global_auto_unwrap={}):
	assert s.count('=') == 1
	ctype = None
	decl, val = s.split('=')
	if val.endswith(';'):
		val = val[:-1]
	decl = decl.strip()
	val = val.strip()
	assert ' ' not in decl
	if val.isdigit():
		ctype = 'long'
	elif val.count('"')==2 and decl.count('[')==1 and decl.count(']')==1:
		ctype = 'char'
	elif val == "''":
		ctype = 'char'
	elif val == 'False' or val == 'True':
		ctype = 'tp_obj' #'bool'
	elif val == 'None':
		ctype = 'tp_obj'
	elif val.startswith('['):
		ctype = 'std::vector<tp_obj>'
		#not safe yet#ctype = 'tp_obj'
	elif classes:
		for classname in classes:
			if classname in val:
				#ctype = classname
				ctype = 'tp_obj'
				global_auto_unwrap[ decl ] = classname
				break

	if val.startswith('ord(') and val.endswith(')'):
		ctype = 'int'
	elif val.endswith(')') and '(' in val:  ## some function call
		ctype = 'tp_obj'
	elif val.endswith('*'):  ## some pointer
		ctype = val

	if ctype:
		if decl not in __guesses:
			__guesses[decl] = ctype
		return (ctype, decl, val)
	elif val in __guesses:
		return (__guesses[val], decl, val)

	print('--------classes----------')
	print(classes)
	print('--------prev guesses-----')
	print(__guesses)
	raise RuntimeError('can not guess type for: ' + s)

def get_base_members( classes, class_name, base_members={} ):
	#for m in classes[class_name]:
	base_members.update( classes[class_name]['members'] )
	for base in classes[class_name]['bases']:
		if base in ('tp_obj', 'tpy_subclass'):
			continue
		get_base_members( classes, base, base_members )

tpy_modules_aot = {}

def pythonicpp( source, header='', file_name='', info={}, swap_self_to_this=False, binary_scramble=False, mangle_map=None, fodg=None, unreal_plugin_name=None, vis_cursor=None, mode='c++' ):
	if not type(source) is list:
		source = source.splitlines()
	print(file_name)
	if file_name.endswith('.aot.pyh'):
		tpy_modules_aot[file_name] = source
		return None

	if type(fodg) is list:
		fodg.append('<?xml version="1.0" encoding="UTF-8"?>')
		fodg.append('<office:document xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" xmlns:presentation="urn:oasis:names:tc:opendocument:xmlns:presentation:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0" xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0" xmlns:math="http://www.w3.org/1998/Math/MathML" xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0" xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0" xmlns:ooo="http://openoffice.org/2004/office" xmlns:ooow="http://openoffice.org/2004/writer" xmlns:oooc="http://openoffice.org/2004/calc" xmlns:dom="http://www.w3.org/2001/xml-events" xmlns:xforms="http://www.w3.org/2002/xforms" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:smil="urn:oasis:names:tc:opendocument:xmlns:smil-compatible:1.0" xmlns:anim="urn:oasis:names:tc:opendocument:xmlns:animation:1.0" xmlns:rpt="http://openoffice.org/2005/report" xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:grddl="http://www.w3.org/2003/g/data-view#" xmlns:officeooo="http://openoffice.org/2009/office" xmlns:tableooo="http://openoffice.org/2009/table" xmlns:drawooo="http://openoffice.org/2010/draw" xmlns:calcext="urn:org:documentfoundation:names:experimental:calc:xmlns:calcext:1.0" xmlns:loext="urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0" xmlns:field="urn:openoffice:names:experimental:ooo-ms-interop:xmlns:field:1.0" xmlns:formx="urn:openoffice:names:experimental:ooxml-odf-interop:xmlns:form:1.0" xmlns:css3t="http://www.w3.org/TR/css3-text/" office:version="1.2" office:mimetype="application/vnd.oasis.opendocument.graphics">')
		fodg.extend([
			'<office:settings>',
			'<config:config-item-set config:name="ooo:view-settings">',
			'<config:config-item config:name="VisibleAreaTop" config:type="int">560</config:config-item>',
			'<config:config-item config:name="VisibleAreaLeft" config:type="int">156</config:config-item>',
			'<config:config-item config:name="VisibleAreaWidth" config:type="int">29131</config:config-item>',
			'<config:config-item config:name="VisibleAreaHeight" config:type="int">14711</config:config-item>',
			'</config:config-item-set>',
			'</office:settings>',

			'<office:automatic-styles>',
			'<style:page-layout style:name="PAGELAYOUT">',
			'<style:page-layout-properties fo:margin-top="1cm" fo:margin-bottom="1cm" fo:margin-left="1cm" fo:margin-right="1cm" fo:page-width="21.59cm" fo:page-height="27.94cm" style:print-orientation="portrait"/>',
			'</style:page-layout>',

			'<style:style style:name="LIGHTBLUE" style:family="paragraph">',
			'<loext:graphic-properties draw:fill-color="#e8f2a1"/>',
			'<style:paragraph-properties fo:text-align="center"/>',
			'</style:style>'
			'<style:style style:name="RED" style:family="paragraph">',
			'<loext:graphic-properties draw:fill-color="#ff0000"/>',
			'<style:paragraph-properties fo:text-align="center"/>',
			'</style:style>'
			'<style:style style:name="GREEN" style:family="paragraph">',
			'<loext:graphic-properties draw:fill-color="#00ff00"/>',
			'<style:paragraph-properties fo:text-align="center"/>',
			'</style:style>'
			'<style:style style:name="BLUE" style:family="paragraph">',
			'<loext:graphic-properties draw:fill-color="#0000ff"/>',
			'<style:paragraph-properties fo:text-align="center"/>',
			'</style:style>'
			'<style:style style:name="YELLOW" style:family="paragraph">',
			'<loext:graphic-properties draw:fill-color="#ffff00"/>',
			'<style:paragraph-properties fo:text-align="center"/>',
			'</style:style>'
			'<style:style style:name="PURPLE" style:family="paragraph">',
			'<loext:graphic-properties draw:fill-color="#ff00ff"/>',
			'<style:paragraph-properties fo:text-align="center"/>',
			'</style:style>'
			'<style:style style:name="BLACK" style:family="paragraph">',
			'<loext:graphic-properties draw:fill-color="#000000"/>',
			'<style:paragraph-properties fo:text-align="center"/>',
			'</style:style>'
			'<style:style style:name="WHITE" style:family="paragraph">',
			'<loext:graphic-properties draw:fill-color="#ffffff"/>',
			'<style:paragraph-properties fo:text-align="center"/>',
			'</style:style>'


			'<style:style style:name="PAGESTYLE" style:family="drawing-page">',
			'<style:drawing-page-properties draw:background-size="border" draw:fill="none"/>',
			'</style:style>',

			'<style:style style:name="DEF" style:family="text">',
			'<style:text-properties fo:font-size="14pt" style:font-size-asian="14pt" style:font-size-complex="14pt"/>',
			'</style:style>',

			'<style:style style:name="FUNC" style:family="text">',
			'<style:text-properties fo:font-size="18pt" style:font-size-asian="18pt" style:font-size-complex="18pt" fo:background-color="#000000" fo:color="#00ff00"/>',
			'</style:style>',
			'</office:automatic-styles>',
			'<office:master-styles>',
			'<style:master-page style:name="Default" style:page-layout-name="PAGELAYOUT" draw:style-name="PAGESTYLE"/>',
			'</office:master-styles>',

			'<office:body>',
			'	<office:drawing>',
			'		<draw:page draw:name="page1" draw:master-page-name="Default">',
		])
	out = []
	if header:
		out.append(header)

	prev = ''
	prevs = ''
	previ = -1
	autobrace = 0
	autofunc = 0
	mods = {'__aot_builtin_module__':[]}
	modname = None
	init_list = []
	in_init_list = False
	init_list_indent = 0
	in_class = False
	class_members = {}
	class_con = []
	class_new = []
	in_struct = False
	struct_stack = []
	struct_name = None
	struct_indent = 0
	in_enum = False
	enum_indent = 0
	class_indent = 0
	class_name = None
	class_has_init = False
	classes = {}
	tp_obj_subclass = False
	nsbrace = -1
	lambdabrace = []
	define = []
	define_ident = -1
	func_name = None
	in_func = False
	is_virt = False
	auto_unwrap = {}
	global_auto_unwrap = {}
	func_indent = -1
	func_locals = {}
	func_globals = []
	func_info = {'name':None, 'args':[], 'returns':None}
	virt_func_dispatch = {}
	fodgx = -16
	fodgy = 0
	fid = 0
	in_vis = True
	macro_indent = []
	in_unreal_plugin = False
	unreal_plugin_cpp = []
	unreal_plugin_iface = []
	unreal_blueprints = {}
	in_blueprint = False
	unreal_blueprint = []
	extern_funcs = []
	em_js = False
	next_line = ''
	user_pythonic = file_name.endswith('__user_pythonic__.pyh')

	if user_pythonic:
		#out.append('#define unwrap(T,o) ((T*)o.pointer.val)')
		out.append('#define unwrap(T,o) static_cast<T*>(o.pointer.val)')
		# why do these macros sometimes fail with this error?
		#error: expected ‘>’ before ‘*’ token #define unwrap(T,o) static_cast<T*>(o.pointer.val)

		if tpy_modules_aot:
			src = []
			for aotmod in tpy_modules_aot:
				#src.extend( tpy_modules_aot[aotmod] )
				for ln in tpy_modules_aot[aotmod]:
					src.append('\t' + ln)

			src.extend( source )
			source = src
			tpy_modules_aot.clear()

	if 'functions' in info:
		functions = info['functions']
	else:
		functions = {}

	for line_num, ln in enumerate(source):
		if line_num+1 < len(source):
			next_line = source[line_num+1]
		oline = ln
		draw_type = 'rectangle'
		color = 'LIGHTBLUE'
		if '(' in ln and ')' in ln:
			draw_type= 'round-rectangle'
		if vis_cursor:
			if line_num + 40 > vis_cursor[0]:
				in_vis = False
			elif line_num < vis_cursor[0]:
				in_vis = False
			else:
				in_vis = True
		indent = 0
		for c in ln:
			if c == '\t':
				indent += 1
			else:
				break

		if in_blueprint:
			unreal_blueprint.append(ln)
			if not ln.strip():
				in_blueprint = False
			continue

		## curved upwards arrow is a reference
		if u'⤴' in ln:
			ln = ln.replace(u'⤴', '&')
		## black rightwards arrow head is a pointer
		if u'⮞' in ln:
			ln = ln.replace(u'⮞', '*')
		if u'×' in ln:
			ln = ln.replace(u'×', '*')
		if u'÷' in ln:
			ln = ln.replace(u'÷', '/')
		if u'≼' in ln:
			ln = ln.replace(u'≼', '<')
		if u'≽' in ln:
			ln = ln.replace(u'≽', '>')
		if u'🔒' in ln:
			ln = ln.replace(u'🔒', ' const ')
		if u'🠊' in ln:
			ln = ln.replace(u'🠊', '->')
		if u'⧟' in ln:
			ln = ln.replace(u'⧟', ',')

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

		if macro_indent and indent <= macro_indent[-1]:
			if 'else:' in s:
				if indent < macro_indent[-1]:  ## TODO support more nested levels
					out.append(('\t'*macro_indent.pop())+'#endif')
				out.append(('\t'*indent)+'#else')
			else:
				out.append(('\t'*macro_indent.pop())+'#endif')

		elif not len(define):
			if in_init_list and indent <= init_list_indent:
				if not out[-1][-1] == '{':
					for outln in out:
						print(outln)
					raise SyntaxError("invalid init_list: syntax")
				out[-1]  = out[-1][:-1]
				out[-1] += ' : ' + ', '.join(init_list) + ' {'
				in_init_list = False
				init_list_indent = 0
				init_list = []
			######################################################
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
			elif macro_indent and indent <= macro_indent[-1]:
				out.append( ('\t'*macro_indent.pop())+"#endif" )
			elif indent < previ and autobrace:
				braces = previ - indent
				b = '\t' * indent

				if in_func and indent <= func_indent and user_pythonic:
					#if indent == func_indent:
					#	b += 'return None;}'
					#else:
					b += '}' * ((previ - func_indent)-1)
					if func_info['returns'] == 'tp_obj':
						b += 'return None;}'
					else:
						b += '}'
					b += '// end of function: %s ' %func_name
					in_func = False
					func_indent = -1
				else:
					b += '}'*braces
				out.append(b)
				if indent == 0 and in_unreal_plugin:
					out[-1] += ';'
				if indent <= 1 and in_func and em_js:
					out[-1] += ');'
					em_js = False

			############################################
			if in_class and indent <= class_indent:
				in_class = False
				class_indent = 0
				if not out[-1][-1] == '}':
					if class_con:
						out.extend(class_con)
					out.append('}')
				elif class_con:
					out[-1] = out[-1][:-1]  ## trim ending of class }
					out.extend(class_con)
					out.append('}')         ## put back ending of class }

				#out.append('	;// end of class: ' + class_name)
				out[-1] += ';	// end of class: `%s` - members: %s' %(class_name, ', '.join(class_members.keys()))

				if user_pythonic and class_new:
					## generated myclass_new
					out.extend(class_new)

				if class_members and user_pythonic:
					cindex = 0
					found = False
					for oln in out:
						if oln.startswith('class %s:' %class_name):
							found = True
							break
						cindex += 1
					if found:
						base_members = {}
						get_base_members( classes, class_name, base_members )
						members = ['public:']
						for mname in class_members:
							if mname not in base_members:
								members.append(
									'%s %s;' %(class_members[mname], mname)
								)
						out.insert(cindex+1, '\n'.join(members))
					else:
						raise RuntimeError('could not find class def for: ' + class_name)
					classes[class_name]['members'].update(class_members)
					class_members = {}
				class_name = None
				class_con = []
				class_new = []

			elif in_struct and indent <= struct_indent:
				if not out[-1].endswith('}'):
					out[-1] += '}'
				if '.' in struct_name:
					## inline struct def, with variable name at the end
					struct_name, struct_var_name = struct_name.split('.')
					out[-1] += '%s;	// end of struct: %s' %(struct_var_name, struct_name)
				else:
					out[-1] += ';	// end of struct: ' + struct_name
				struct_stack.pop()
				if len(struct_stack):
					struct_name   = struct_stack[-1][0]
					struct_indent = struct_stack[-1][1]
				else:
					in_struct = False
					struct_name = None
					struct_indent = 0
			elif in_enum and indent <= enum_indent:
				if enum_name == 'enum':
					enum_name = 'unnamed'
				if out[-1][-1] == '}':
					out[-1] += ';	// end of enum: ' + enum_name
				else:
					out.append('')  ## just incase there is an #endif at the end of the enum
					out[-1] += '};	// end of enum: ' + enum_name
				in_enum = False


		if not s:
			in_class = False
			if in_func and fodg and in_vis:
				#fodg.append('<draw:enhanced-geometry svg:viewBox="0 0 21600 21600" draw:type="rectangle" draw:enhanced-path="M 0 0 L 21600 0 21600 21600 0 21600 0 0 Z N"/>')
				#fodg.append('</draw:custom-shape>')
				fodgx += 10

			in_func = False
			em_js = False
			func_locals = {}
			func_globals = []
			is_virt = False
			auto_unwrap = {}
			auto_unwrap.update(global_auto_unwrap)

		if user_pythonic and not s.startswith('#') and not s.endswith(";"):
			newln = []
			for part in s.split():
				if part.count('.')==1 and not part.startswith( ('self.', '(self.') ):
					a,b = part.split('.')
					aorig = a
					if a in auto_unwrap:
						if auto_unwrap[a] != "__EXTERNAL_OBJECT__":
							a = 'unwrap(%s,%s)' %(auto_unwrap[a], a)
					#elif is_virt:
					elif in_func:
						hits = []
						for clsname in classes:
							if b.split('[')[0] in classes[clsname]['members']:
								hits.append(clsname)
								## https://stackoverflow.com/questions/3786360/confusing-template-error
								a = a + ('.template unwrap<class %s>()' %clsname)
								## above template workaround is ugly, and sometimes still fails with error: use of ‘this’ in a constant expression,
								## this happens when the class contains a member with the same name as the class being casted to,
								## by prefixing `class ` the problem is solved.
								##a = 'unwrap(%s,%s)' %(clsname, a)
							elif '(' in b:
								if b.split('(')[0] in classes[clsname]['methods']:
									hits.append(clsname)
									a = a + ('.template unwrap<class %s>()' %clsname)
									#a = 'unwrap(%s,%s)' %(clsname, a)
						if not hits and in_class:
							## checks own class members
							if b.split('[')[0] in class_members:
								hits.append(class_name)
								a = a + ('.template unwrap<%s>()' %class_name)
							elif '(' in b:
								if b.split('(')[0] in class_members:
									hits.append(class_name)
									a = a + ('.template unwrap<%s>()' %class_name)

						if not hits and '(' not in a and a not in classes and '->' not in a:
							if b.startswith( ('set(','append(') ):
								## tp_obj base class contains a set and append methods
								pass
							elif b.startswith( ('size(', 'clear(', 'push_back(') ):
								## std::vector, std::string, and other c++11 containers
								pass
							elif b.isdigit():
								pass
							elif a.isdigit():
								pass
							elif a.startswith('-') and len(a) >= 2 and a[1:].isdigit():
								pass
							elif a.startswith('&'):
								## lower level pythonic++ must sometimes be used in AOT code
								pass
							elif s.startswith('switch '):
								pass
							else:
								print('parse error')
								print(b)
								print(s)
								print(part)
								print(class_members)
								raise RuntimeError("unable to find the class type from member or method use on variable: `%s`" %a)		
						elif len(hits) > 1:
							raise SyntaxError('can not auto unwrap a pointer because multiple classes have the same named members or methods: %s line: `%s`' %(str(hits), s))
						elif len(hits) == 1:
							## not very safe or required to remove *most* of the need for pythonic users to manually use @unwrap
							if aorig.startswith('('):
								aorig = aorig[1:]
							if aorig not in auto_unwrap:
								if '(' in aorig or ')' in aorig:
									#raise SyntaxError(part)
									print('WARN: parser choked on `%s` from line: `%s` ' % (aorig, s) )
								else:
									# the problem with this magic is that a base class with the member could have been picked first
									# then later when the variable is used again, its auto_unwrapp'ed as the base class, 
									# and not the required subclass type.
									#auto_unwrap[aorig] = hits[0]
									pass

					if a != part.split('.')[0]:
						newln.append('%s->%s' %(a,b))
					else:
						newln.append(part)
				else:
					clsnames = list( classes )
					clsnames.sort()
					clsnames.reverse()
					for clsname in clsnames:
						if part.startswith(clsname+'('):
							part = part.replace(clsname+'(', clsname+'_new(')
							if s.count('=') == 1:
								a,b = s.split('=')
								a = a.strip()
								if '.' not in a:
									if a in auto_unwrap and auto_unwrap[a] != clsname:
										raise RuntimeError("auto unwrap error - type redefined : `%s`" %s)
									auto_unwrap[a] = clsname
							break
					newln.append(part)
			s = ' '.join(newln)
			ln = ('\t'*indent) + s

		if s.startswith('##'):
			ln = ln.replace('##', '//')
			out.append(ln)
		elif user_pythonic and s.startswith("#"):
			## note user can not directly use macro syntax
			pass
		elif s.startswith("global "):
			## using the global keyword in low level pythonic++ (used to implement the VM) is just for clarity, local vars are not auto prefixed, it is done manually ##
			func_globals = [gbl.strip() for gbl in s.split('global ')[-1].split(',')]
			pass
		elif user_pythonic and s.startswith("raise "):
			## currently not used in low level pythonic++ (used to implement the VM)
			if 'NotImplementedError' in s:
				## forced to be forward declared and defined later, using virt_func_dispatch
				indent = previ
			else:
				err = s.split('raise ')[-1]
				out.append('throw "%s";' % err.replace('"', "`"))
		#elif user_pythonic and indent==1 and not ln.startswith(' ') and not s.startswith('@') and is_untyped_global_var(s):
		elif user_pythonic and indent <= 1 and not ln.startswith(' ') and not s.startswith('@') and is_untyped_global_var(s):
			ctype, cname, cval = guess_type_of_var(s, classes=classes, global_auto_unwrap=global_auto_unwrap)
			## check if ctype needs to be a const or a define, if used in a switch/case or an array decl size
			requires_const = False
			requires_define = False
			for line in source:
				if cname in line and 'case ' in line and ':' in line:
					#requires_const = True  ## a const is vaild for use in a switch/case, but a define is better
					requires_define = True
				if cname in line and '[' in line and ']' in line:
					if cname in line.split('[')[-1].split(']')[0]:
						## just because its in brackes it is not for sure that's its an array decl size
						if '=' in line:
							pass
						elif '&'+cname in line.split():
							pass
						else:
							requires_define = True
							break
			if requires_define:
				out.append('#define ' + cname + ' ' + cval)
			else:
				if requires_const:
					ctype = 'const ' + ctype
				out.append(ctype + ' ' + s + ';')
		elif s.startswith('unreal.blueprint') and s.endswith(':'):
			in_blueprint = True
			blueprint_name = s.split('(')[-1].split(')')[0].strip()
			unreal_blueprint = unreal_blueprints[blueprint_name] = []

		elif s == 'unreal.plugin:':
			if not unreal_plugin_name:
				if '.unreal/' in file_name:
					unreal_plugin_name = os.path.split(file_name.split('.unreal/')[0])[-1]
				else:
					raise RuntimeError(file_name)
			in_unreal_plugin = True
			unreal_plugin_lib = list(out)
			out = []
			unreal_plugin_cpp.append('#include "%sPrivatePCH.h"' %unreal_plugin_name)
			unreal_plugin_cpp.append('#include "I%s.h"' %unreal_plugin_name)
			for efunc in extern_funcs:
				unreal_plugin_cpp.append(efunc)
			unreal_plugin_cpp.append('class F%s: I%s {' %(unreal_plugin_name, unreal_plugin_name))

			unreal_plugin_iface.append(UIFACE_TEMPLATE % tuple([unreal_plugin_name]*5) )


		elif s.startswith('import '):
			inc = s.split()[-1]
			if mode=='js':
				if inc == 'THREE':
					threepath = os.path.expanduser('~/three.js')
					if not os.path.isdir(threepath):
						raise RuntimeError(THREEJS_MISSING)
					dat = open(os.path.join(threepath, 'build/three.min.js')).read()
					info['js_header'].append(dat)
			else:
				if inc.startswith("<"):
					assert inc.endswith(">")
				elif not inc.startswith('"'):
					inc = '"' + inc + '"'
				out.append(('\t'*indent)+'#include ' + inc)
		elif s.startswith('define('):
			assert s.endswith(')')
			if '=' in s:
				defname = s[len('define(') : s.index('=') ]
				defval  = s[ s.index('=')+1 : -1]
				out.append('#define %s %s' %(defname, defval))
			else:
				defname = s[len('define(') : -1]
				out.append('#define %s' %defname)
		elif s.startswith('define ') and s.endswith(':'):
			define_ident = indent
			defname = s[len('define ') : -1 ]
			define.append('#define %s \\' %defname)
			continue
		elif s == 'init_list:':
			init_list_indent = indent
			init_list = []
			in_init_list = True
		elif in_init_list:
			if s.endswith(','):
				s = s[:-1]
			init_list.append(s)
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

		elif s.strip() == 'pass':
			out.append('/*pass*/')

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
		elif s.startswith('@unwrap('):
			pass
		elif s == '@constexpr':
			out.append('constexpr')
		elif s in ('@javascript', '@js'):
			em_js = True
		elif s.startswith('@template('):
			out.append( 'template<%s>' % s[len('@template(') : -1] )
		elif s.startswith('@virtual'):
			out.append( 'virtual' )
		elif s.startswith('@UCLASS'):
			out.append( 'UCLASS' )
		elif s.startswith('@UFUNCTION'):
			out.append( s[1:] )
		elif s == '@export.C' or s == '@extern.C':
			out.append( 'extern "C"' )
		elif s == '@export' or s == '@extern':
			out.append( 'extern ' )
		elif s == '@inline':
			out.append( 'inline ' )
		elif s.startswith('@'):
			raise SyntaxError( 'Unknown decorator syntax: ' + s )
		elif ' def[' in s and ln.endswith(':'):
			ln = ln.replace(' def[', '[')
			ln = ln[:-1]+ '{'
			lambdabrace.append(indent)
			out.append(ln)
			draw_type = 'flowchart-stored-data'
			color = "GREEN"

		elif s.startswith('namespace ') and s.endswith(':'):
			assert not nsbrace  ## no nested namespace defs
			nsbrace = indent
			out.append( ('\t'*indent) + s[:-1] + '{')
			autobrace = 0
			draw_type = 'flowchart-direct-access-storage'
		elif s.startswith('namespace ') and s.endswith('{'):
			out.append( ln )
			autobrace = 0
			draw_type = 'flowchart-direct-access-storage'

		elif s.startswith('enum') and s.endswith(':'):
			in_enum = True
			enum_name = s.split()[-1][:-1].strip()
			enum_indent = indent
			if enum_name != 'enum':
				out.append( ('\t'*indent)+'enum %s {' %enum_name)
			else:
				## unnamed enum
				out.append( ('\t'*indent)+'enum {')
		elif in_enum:
			if not s.endswith(',') and not s.startswith('#'):
				s += ','
			out.append('	' + s)

		elif s.startswith('struct') and s.endswith(':'):
			in_struct = True
			struct_name = s.split()[-1][:-1]
			struct_stack.append( [struct_name,indent] )
			struct_indent = indent
			if '.' in struct_name:  ## dot syntax for a named struct with a var name
				out.append( ('\t'*indent)+'struct %s {' %struct_name.split('.')[0])
			else:
				out.append( ('\t'*indent)+'struct %s {' %struct_name)

		elif s.startswith('class') and s.endswith(':'):
			in_class = True
			class_indent = indent
			class_name = s[:-1].split()[-1].strip()
			#class_members = {}
			base_classes = []
			tp_obj_subclass = False
			if s.count('(')==1 and s.count(')')==1:
				class_name = s.split('(')[0].strip().split()[-1]
				for base_class in s.split('(')[-1].split(')')[0].split(','):
					base_class=base_class.strip()
					if base_class == 'object':
						assert user_pythonic
						#base_class = 'tp_obj'
						base_class = 'tpy_subclass'
					base_classes.append(base_class)
				if 'tp_obj' in base_classes:
					tp_obj_subclass = True
			#classes[ class_name ] = {'methods':{}, 'vmethods':{}, 'members':class_members, 'bases':base_classes, 'id':len(classes)+1}
			classes[ class_name ] = {'methods':{}, 'vmethods':{}, 'members':{}, 'bases':base_classes, 'id':len(classes)+1}
			if len(base_classes):
				out.append( 'class %s: public %s {' %(class_name, ','.join(base_classes)))
			elif user_pythonic:
				#out.append( 'class %s: public tp_obj {' % class_name )
				out.append( 'class %s: public tpy_subclass {' % class_name )
			else:
				out.append( 'class %s {' %class_name)
			out.append( '	public:')

		elif s.startswith('def '):
			func_indent = indent
			in_func = True
			func_locals = {}
			func_globals = []
			func_info = {'name':None, 'args':[], 'returns':None}
			is_forward_decl = False
			if s.endswith(';'):
				is_forward_decl = True
			else:
				if not s.endswith( ':' ):
					raise SyntaxError(ln)
				autobrace += 1
				autofunc += 1

			func_name = s[len('def ') : ].split('(')[0].strip()
			func_info['name'] = func_name
			if in_unreal_plugin:
				assert func_name in ('StartupModule', 'ShutdownModule')

			is_constructor = False
			is_destructor = False
			if func_name.count('::')==1:
				a,b = func_name.split('::')
				if a==b:
					is_constructor = True
					func_info['constructor'] = True
				elif b.startswith('~') and a == b[1:]:
					is_destructor = True
					func_info['destructor'] = True

			if next_line and 'raise NotImplementedError' in next_line and in_class:
				func_info['virt'] = True
				is_virt = True
				is_forward_decl = True
				assert s.endswith(':')
				s = s[:-1] + ';'
				in_func = False
				func_indent = 0
				if class_name not in virt_func_dispatch:
					virt_func_dispatch[class_name] = {}
				virt_func_dispatch[class_name][func_name] = {'args':[], 'code':[]}
			else:
				is_virt = False

			is_scram = False
			unscram_name = None
			is_init  = False
			
			if in_class and user_pythonic and not func_name.startswith('__'):
				#if class_name not in ('tp_obj', 'tpy_subclass'):
				for base in classes[class_name]['bases']:
					if base in ('tp_obj', 'tpy_subclass'):
						continue
					if func_name in classes[base]['vmethods']:
						is_virt = True
						break
					for base2 in classes[base]['bases']:
						if base2 == 'tp_obj':
							continue
						if func_name in classes[base2]['vmethods']:
							is_virt = True
							break

			if func_name == '__init__':
				assert in_class or in_struct
				is_init = True
				if in_struct:
					func_name = struct_stack[-1][0]
					struct_name = func_name
				else:
					func_name = class_name
				if user_pythonic:
					func_name += '__init__'
			elif not in_class and func_name in functions and 'scramble' in functions[func_name]:
				is_scram = True
				unscram_name = func_name
				func_name = functions[func_name]['scramble']

			if '->' in s:
				returns = s[:-1].split('->')[-1]
			elif in_class and func_name == class_name:
				returns = ''
				class_has_init = True
			elif in_struct and func_name == struct_name:
				returns = ''
			elif prevs.startswith('@module') or (in_class and tp_obj_subclass):
				returns = 'tp_obj'
			elif 'operator' in func_name or is_constructor or is_destructor:
				returns = ''
			elif user_pythonic:
				returns = 'tp_obj'
			else:
				returns = 'void'
				
			func_info['returns'] = returns

			if prevs.startswith('@module'):
				args = ['TP']
				tpargs = []
			else:
				args = []

			#rawargs = s.split('(')[-1].split(')')[0]
			try:
				rawargs = s.split('->')[0][ s.index('(')+1 : s.rindex(')') ]
			except ValueError:
				raise SyntaxError(s)
			arg_types = []
			func_post = []
			auto_templates = []
			for i, arg in enumerate(rawargs.split(',')):
				arg = arg.strip()
				if not arg:
					continue

				if in_class and user_pythonic:
					if i==0:
						assert arg == 'self'
					else:
						if ' ' in arg:
							args.append(arg)
						elif is_virt:
							args.append('tp_obj '+arg)
						else:
							auto_templates.append(arg)
							arg = 'T_%s %s' % (len(auto_templates)-1, arg)
							args.append(arg)

				elif in_class and tp_obj_subclass:
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
							## rule: `__init__(self, names...)` where names must be the member names,
							## not used by higher level user pythonic AOT scripts.
							if func_name == class_name and not user_pythonic:
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
					if mode=='js':
						pass
					elif em_js:
						if ' ' not in arg:
							raise SyntaxError('@javascript functions must define a type for each argument')
						atype = arg[ : arg.rindex(' ') ].strip()
						aname = arg.split()[-1]
						pointers = aname.count('*')
						if aname.endswith(']'):
							raise SyntaxError('@javascript function arguments can not be of an array type')
						if pointers:
							atype += '*' * pointers
							aname = aname.replace('*', '')
						else:
							arg_types.append(atype)

						if atype == 'const char*':
							arg = '%s __%s__' %(atype, aname)
							func_post.append('var %s = UTF8ToString(__%s__);' %(aname, aname) )
						elif atype not in ('void*', 'int', 'float'):
							raise SyntaxError('@javascript function invalid argument type: %s' %arg)

					elif ' ' not in arg and arg != 'TP' and arg != 'void' and arg != '...' and arg != 'VARIANT_ARG_DECLARE':
						## clang can not use auto for func params :(
						if user_pythonic:
							auto_templates.append(arg)
							arg = 'T_%s %s' % (len(auto_templates)-1, arg)
						else:
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


			if fodg and in_vis:
				fid += 1
				fodgy = 0
				fodg.append(
					'<draw:custom-shape draw:text-style-name="GREEN" xml:id="id%s" draw:id="id%s" draw:layer="layout" svg:width="14.224cm" svg:height="8.001cm" svg:x="%scm" svg:y="%scm">' %(fid, fid, fodgx, fodgy)
				)
				fodg.append('<text:p><text:span text:style-name="FUNC">%s</text:span></text:p>' %escape(func_name))
				for aidx, arg in enumerate(args):
					arg = arg.replace('*', u'⮞').replace('&', u'⤴')
					fodg.append('<text:p><text:span text:style-name="DEF"> ⟹ %s</text:span></text:p>' %escape(arg))
				fodg.append('<text:p><text:span text:style-name="DEF"> ⟸ %s</text:span></text:p>' %escape(returns))
				fodg.append('<draw:enhanced-geometry draw:type="cube"/>')
				fodg.append('</draw:custom-shape>')
				#groups.append([fodgx])
				draw_type = 'cube'
				fodgy += len(args) * 1.5
				fodgy += 1


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

			if auto_templates:
				out.append('template<' + ','.join( ['typename T_%s' %i for i in range(len(auto_templates))] ) + '>')

			func_info['args'] = args

			exopts = ''
			if prevs == '@const':
				exopts = ' const '
			if prevs == '@static':
				returns = 'static ' + returns

			auto_unwrap = {}
			auto_unwrap.update(global_auto_unwrap)

			if prevs.startswith('@unwrap('):
				for part in prevs.strip()[len('@unwrap(') : -1].split(','):
					assert '=' in part
					a,b = part.split('=')
					a = a.strip()
					b = b.strip()
					if b.startswith("'") and b.endswith("'"):
						b = b[1:-1]
					elif b.startswith('"') and b.endswith('"'):
						b = b[1:-1]
					auto_unwrap[ a ] = b

			if is_virt:
				assert not auto_templates
				#returns = 'virtual ' + returns

			if in_class:
				func = '\t' * indent
			else:
				func = '\t'

			if in_unreal_plugin:
				assert len(args)==0
				func += 'virtual %s() override {' %func_name

			elif is_forward_decl:
				if user_pythonic:
					if in_class and is_virt:
						func += '%s %s(%s) %s;' %(returns, func_name, ','.join(args), exopts)
						virt_func_dispatch[class_name][func_name]['args'] = args
						virt_func_dispatch[class_name][func_name]['code'].extend([
							'%s %s::%s(%s) %s{' %(returns, class_name, func_name, ','.join(args), exopts),
							'	switch (this->pointer.classid) {',
						])
					else:
						raise RuntimeError("TODO user pythonic forward declared function")
				else:
					if in_class and func_name == class_name:
						func += '%s(%s) %s;' %(func_name, rawargs, exopts)
					else:
						func += '%s %s(%s) %s;' %(returns, func_name, rawargs, exopts)
			elif mode=='js':
				func += '%s=function(%s){' %(func_name, ','.join(args))
				if 'js_funcs' in info:
					if returns in ('int', 'float', 'double', 'string', 'void'):
						info['js_funcs'][func_name] = {'returns':returns, 'args':args}

			elif em_js:
				if in_class:
					raise SyntaxError('@javascript functions can not defined inside a class')
				func += 'EM_JS(%s, %s, (%s), {' %(returns, func_name, ','.join(args))

			else:
				if in_class and func_name == class_name:
					func += '%s(%s) %s{' %(func_name, ','.join(args), exopts)
				elif in_class and is_init and user_pythonic:
					func += '%s %s(%s) %s{' %(returns, func_name, ','.join(args), exopts)
					if auto_templates:
						class_con.append('template<' + ','.join( ['typename T_%s' %i for i in range(len(auto_templates))] ) + '>')
						class_new.append('template<' + ','.join( ['typename T_%s' %i for i in range(len(auto_templates))] ) + '>')

					class_con.extend([
						'%s(%s) %s{' % (class_name, ','.join(args), exopts),
						#'	print("new class %s");' %class_name,
						'	this->type.type_id = TP_POINTER;',
						'	this->pointer.classid  = %s;' %classes[class_name]['id'] ,
						#'	this->pointer.val  = (void*)this;',
						#'	print(this);',
						'	this->%s__init__(%s);' % (class_name, ','.join(auto_templates)),
						'}'
					])
					class_new.extend([
						## it is not safe to return a copy of the class, because changes made to it will not be updated in obj->pointer.val
						#'%s %s_new(%s) {' % (class_name, class_name, ','.join(args)),
						## it is safe to return a tp_obj as a copy, which simply holds a pointer to the new object
						'tp_obj %s_new(%s) {' % (class_name, ','.join(args)),
						'	%s* obj = new %s(%s);' % (class_name, class_name, ','.join(auto_templates)),
						'	obj->pointer.val = (void*)obj;',
						#'	return *obj;',  ## do not return a copy
						'	return *(tp_obj*)obj;',
						'}'
					])
					## generate tpython interpreter wrapper function ##
					if not class_name.startswith('_'):
						mods['__aot_builtin_module__'].append([
							class_name,
							'__tpy_%s_new' %class_name,
						])
						class_new.append('tp_obj __tpy_%s_new(TP) {' % class_name )
						for arg in auto_templates:
							class_new.append('	tp_obj %s = TP_OBJ();' % arg )
						class_new.extend([
							'	return %s_new(%s);' % (class_name, ','.join(auto_templates)),
							'}'
						])

					if len(args):
						## also generate default constructor
						class_con.extend([
							'%s() %s{' % (class_name, exopts),
							'	this->type.type_id = TP_POINTER;',
							'	this->pointer.val  = (void*)this;',
							'	this->pointer.classid  = %s;' %classes[class_name]['id'] ,
							'}'
						])
					## generate extra helpers ##
					if False:  ## not required
						class_con.extend([
							'%s operator= (tp_obj ob){' % class_name,
							'	print("= op");',
							'	if (ob.type.type_id == TP_NONE)',
							'		this->pointer.val = NULL;',
							'	else throw "operator error `=`";',
							'	return *this;',
							'}'
						])
					## a different return type is not allowed
					##class_con.extend([
					##	'virtual %s get(){' % class_name,
					##	'	return *(%s*)this->pointer.val;' %class_name,
					##	'}'
					##])

				else:
					func += '%s %s(%s) %s{' %(returns, func_name, ','.join(args), exopts)
					if user_pythonic and in_class and is_virt:
						for vclass in virt_func_dispatch:
							if func_name in virt_func_dispatch[vclass]:
								vinfo = virt_func_dispatch[vclass][func_name]
								vargs = [varg.split()[-1] for varg in vinfo['args']]
								vinfo['code'].extend([
									'		case %s: {' %classes[class_name]['id'],
									'			return ((%s*)this->pointer.val)->%s(%s);' %(class_name, func_name, ','.join(vargs)),
									'		} break;'
								])
					elif prevs.startswith( ('@export', '@extern') ):
						sig = 'extern %s %s(%s) %s;' %(returns, func_name, ','.join(args), exopts)
						assert sig not in extern_funcs
						extern_funcs.append(sig)

			out.append(func)
			if func_post:
				out.extend(func_post)

			if prevs.startswith('@module'):
				if is_scram:
					mods[modname].append( {'scram':func_name, 'unscram':unscram_name} )
				else:
					mods[modname].append(func_name)


				out.extend(tpargs)
				
			if in_class and user_pythonic and is_init:
				## generate lambda wrappers
				for methname in classes[ class_name ]['methods']:
					if methname.startswith('_'):
						continue
					methargs = classes[ class_name ]['methods'][methname]
					margs =  ','.join( ['TP_OBJ()' for ma in methargs] )
					#wrapper = '			std::function<tp_obj(tp_vm*)> __%s_wrapper = [=](tp_vm *tp){return this->%s(%s);};' %(methname, methname, margs)
					wrapper = '			std::function<tp_obj(tp_vm*)> __%s_wrapper = [this](tp_vm *tp){return this->%s(%s);};' %(methname, methname, margs)
					out.append(wrapper)
					out.append('			this->__methods__["%s"] = tp_function(__%s_wrapper);' %(methname, methname))

			elif in_class and func_name==class_name and tp_obj_subclass:
				raise RuntimeError("tp_obj_subclass is DEPRECATED - replaced by higher level AOT")
				out.append('			this->type.type_id = TP_OBJECT;')
				out.append('			this->dict.val = tpd_dict_new(tp);')
				out.append('			this->obj.info->meta = tp_None;')
				## generate lambda wrappers
				for methname in classes[ class_name ]['methods']:
					methargs = classes[ class_name ]['methods'][methname]
					margs =  ','.join( ['TP_OBJ()' for ma in methargs] )
					wrapper = '			std::function<tp_obj(tp_vm*)> __%s_wrapper = [=](tp_vm *tp){return this->%s(%s);};' %(methname, methname, margs)
					out.append(wrapper)
					out.append('			tp_set(tp, *this, "%s", tp_function(tp, __%s_wrapper));' %(methname, methname))
			elif in_class:
				classes[ class_name ]['methods'][ func_name ] = args
				if is_virt:
					classes[ class_name ]['vmethods'][ func_name ] = args

		elif s.startswith('switch ') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			w += 'switch(' + s[len('switch '):-1] + ') {'
			out.append(w)
			draw_type = 'flowchart-multidocument'

		elif s.startswith('case ') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			w += 'case ' + s[len('case '):] + '{'
			out.append(w)
			draw_type = 'flowchart-punched-tape'

		elif s == 'default:':
			autobrace += 1
			out.append(ln + '{')
			draw_type = 'flowchart-document'

		elif s.startswith('goto ') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			w += s[len('goto '):] + '{'
			out.append(w)
			draw_type = 'chevron'
			color = "RED"

		elif s.startswith('while ') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			if user_pythonic:
				if ' is not ' in s:
					s = s.replace(' is not ', ' != ')
				elif ' is ' in s:
					s = s.replace(' is ', ' == ')
			w += 'while(' + s[len('while '):-1] + ') {'
			out.append(w)
			draw_type = 'flowchart-preparation'

		elif s.startswith( ('for ', 'for(','for (') ) and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			if s.startswith('for ') and ' in ' in s:  ## python style
				if ' range(' in s:
					assert s.endswith('):')
					#iter_to = s.split('range(')[-1].split(')')[0]
					iter_to = s.split('range(')[-1][:-2]
					iter_name = s.split(' in ')[0].split()[-1]
					if ',' in iter_to:
						iter_start, iter_to = iter_to.split(',')
						w += 'for (int %s=%s; %s<%s; %s++){' %(iter_name, iter_start, iter_name, iter_to, iter_name)
					else:
						w += 'for (int %s=0; %s<%s; %s++){' %(iter_name, iter_name, iter_to, iter_name)
				else:
					iter_name = s.split(' in ')[0].split()[-1]
					auto_unwrap[ iter_name ] = "__EXTERNAL_OBJECT__"
					iterable = s.split(' in ')[-1][:-1]
					w += 'for (auto %s: %s){' %(iter_name, iterable)
					##raise RuntimeError("TODO translate python interator style to c++11 for iter loop\n%s" %w)
			else:  ## c++ style
				loop = s[len('for '):-1]
				if not loop.startswith('('):
					loop = '(' + loop
				if not loop.endswith(')'):
					loop += ')'
				w += 'for ' + loop + ' {'
			out.append(w)
			draw_type = 'flowchart-display'
			color = "PURPLE"

		elif s.startswith('try') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			w += 'try ' + s[len('try'):-1] + ' {'
			out.append(w)

		elif s.startswith('catch ') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			w += 'catch ' + s[len('catch '):-1] + ' {'
			out.append(w)

		elif s.startswith('if not ') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			if 'defined(' in s:
				if s.count('defined(')==2:
					assert ') or defined(' in s
					x, y = s.split(') or defined(')
					x = x.split('defined(')[0]
					y = y[:-2]
					w += '#if %s || %s' %(x,y)
				else:
					w += '#ifndef ' + s.split('defined(')[-1][:-2]
				macro_indent.append(indent)
			else:
				if '&&' in s or '||' in s:
					#if s.count('&&') > 1:
					#	raise SyntaxError('TODO `if not` with multiple &&: %s' %s)
					w += 'if(!' + s[len('if not '):-1] + ') {'
				else:
					w += 'if(!(' + s[len('if not '):-1] + ')) {'
			out.append(w)
			draw_type = 'down-arrow-callout'

		elif s.startswith('if ') and 'defined(' in s and not s.endswith(':'):
			raise SyntaxError('if defined macro missing ending `:` - %s' %s)
		elif s.startswith('if ') and s.endswith(':'):
			w = '\t' * indent
			if 'defined(' in s:
				w += '#ifdef ' + s.split('defined(')[-1][:-2]
				macro_indent.append(indent)
			else:
				if user_pythonic:
					if ' is not ' in s:
						s = s.replace(' is not ', ' != ')
					elif ' is ' in s:
						s = s.replace(' is ', ' == ')
					if 'self.' in s:
						s = s.replace('self.', 'this->')
				if ('==' in s or '!=' in s) and not s.count('('):
					if ' & ' in s:
						raise SyntaxError("using the bitwise & operator without wrapping its operands in `()` is invalid\n" + s)
					elif ' | ' in s:
						raise SyntaxError("using the bitwise | operator without wrapping its operands in `()` is invalid\n" + s)
					elif ' ^ ' in s:
						raise SyntaxError("using the bitwise ^ operator without wrapping its operands in `()` is invalid\n" + s)
				autobrace += 1
				w += 'if(' + s[len('if '):-1] + ') {'
				draw_type = 'down-arrow-callout'
				color = 'BLUE'
			out.append(w)

		elif s.startswith('elif not ') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			if '||' in s:
				raise SyntaxError('TODO `elif not` with ||: %s' %s)
			if '&&' in s or '||' in s:
				#if s.count('&&') > 1:
				#	raise SyntaxError('TODO `elif not` with multiple &&: %s' %s)
				w += 'else if(!' + s[len('if not '):-1] + ') {'
			else:
				w += 'else if(!(' + s[len('elif not '):-1] + ')) {'
			out.append(w)
			draw_type = 'down-arrow-callout'
			color = 'BLUE'

		elif s.startswith('elif ') and s.endswith(':'):
			autobrace += 1
			w = '\t' * indent
			w += 'else if(' + s[len('elif '):-1] + ') {'
			out.append(w)
			draw_type = 'down-arrow-callout'
			color = 'BLUE'

		elif s == 'else:':
			w = '\t' * indent
			if macro_indent and indent <= macro_indent[-1]:
				#w += '#else'
				pass
			else:
				autobrace += 1
				w += 'else {'
				out.append(w)
				draw_type = 'down-arrow-callout'
				color = 'BLUE'

		elif s == 'with scope:':
			autobrace += 1
			w = '\t' * indent
			w += '{ // new scope'
			out.append(w)

		elif user_pythonic and in_class and class_indent+1 == indent and ln.count('='):
			var, val = s.split('=')
			val = val.strip()
			var = var.strip()
			
			class_members[ var ] = val
			ln = '//' + ln

		else:

			if user_pythonic and ln.count('=')==1 and in_func and not s.startswith( ('self.', 'unwrap(', 'print(') ):
				if s.startswith('if ') and s.endswith(';'):
					## c++ style if statement
					pass
				else:
					var, val = s.split('=')
					val = val.strip()
					var = var.strip()
					if var.endswith( ('+', '-', '/', '*') ):
						var = var[:-1].strip()

					if ' ' in var:
						print(ln)
						cpptype = var.split()[ : -1]
						var = var.split()[-1]
						if var.startswith('*'):
							cpptype.append('*')
							var = var[1:]
						assert var not in func_locals
						func_locals[ var ] = cpptype
					elif '.' in var or '->' in var or '[' in var:
						pass
					elif var not in func_locals and var not in func_globals:
						func_locals[var] = val
						ln = 'auto ' + ln

			#if in_class and tp_obj_subclass and swap_self_to_this:
			if in_class and user_pythonic and swap_self_to_this:
				if '.__init__(self,' in ln:
					ln = ln.replace('.__init__(self,', '__init__(')
				elif '.__init__(self)' in ln:
					ln = ln.replace('.__init__(self)', '__init__()')
				if 'self.' in ln:
					if ln.count('=')==1:
						member, val = s.split('=')
						member = member.strip()
						val = val.strip()
						if member.count('.') == 1 and member.startswith('self.'):
							mtype = 'tp_obj'
							mname = member.split('.')[-1].strip()
							if val.startswith('['):
								mtype = 'std::vector<tp_obj>'
								#mtype = 'tp_obj' # crashes
								class_members[ mname ] = mtype
								if val.count('*')==1:
									arrdef, arrmult = val.split('*')
									arrdef = arrdef.strip()
									arrmult = arrmult.strip()
									assert arrdef.count('[')==1 and arrdef.count(']')==1
									arrdef = arrdef.split('[')[-1].split(']')[0].strip()
									#not safe yet TODO#rep = '[](){tp_obj _=tp_list(); for (int i=0; i<%s; i++){_.append(%s);} return _; }();' %(arrmult,arrdef)
									if arrdef == 'None':
										rep = '[](){std::vector<tp_obj> _={}; for (int i=0; i<%s; i++){_.push_back(%s);} return _; }();' %(arrmult,arrdef)
									else:
										rep = '[](){std::vector<tp_obj> _={}; for (int i=0; i<%s; i++){_.push_back(tp_obj(%s));} return _; }();' %(arrmult,arrdef)
									ln = ln.replace( val, rep )
								elif val == '[]':
									ln = ln.replace('[]', 'std::vector<tp_obj>()')
									#not safe yet#ln = ln.replace('[]', 'tp_list()')
							elif val.count('.')==1 and False:  ## not safe
								valob, valmem = val.split('.')
								valob = valob.strip()
								valmem = valmem.strip()
								hits = []
								guess_type = None
								for other_class in classes:
									if other_class == class_name:
										continue
									if valmem.endswith(')'):
										pass  ## TODO search other class methods, and checking return type
									else:
										for other_mem in classes[other_class]['members']:
											if other_mem==valmem:
												hits.append(other_class)
												guess_type = classes[other_class]['members'][valmem]
								if len(hits) == 1:
									class_members[ mname ] = guess_type
								elif len(hits) > 1:
									raise RuntimeError('can not guess member type `%s` because it is used by multiple classes: %s' %(valmem, ','.join(hits)))
								else:
									print('WARNING: can not guess member type of: `%s`' %ln)
							elif mname in class_members and class_members[mname] != 'tp_obj':
								#class_members[ mname ] = mtype
								pass
							else:
								class_members[ mname ] = mtype

					ln = ln.replace('self.', 'this->')

				elif 'return self' in ln:
					ln = ln.replace('return self', 'return *this')
				elif '=' in ln and ln.split('=')[-1].strip()=='self':
					ln = ln.replace('self', '*this')
				elif ',self)' in ln:
					ln = ln.replace(',self)', ',*this)')
					
			ln = auto_semicolon(ln)
			out.append(ln)

		prev = ln
		prevs = s
		previ = indent


		if fodg and in_func and oline.strip() and draw_type != 'cube' and in_vis:
			b = oline.replace('->', u' 🠊 ').replace('<=', u'≤').replace('>=', u'≥').replace('==', u'≡').replace('!=', u'≢')
			b = b.replace('(', u'❪').replace(')', u'❫').replace('{', u'❴').replace('}', u'❵')
			s = b.strip()
			fid += 1
			a = None
			if s.count('=')==1 and not s.startswith( ('for ', 'for(', u'for❪', 'if ', 'while ') ):
				a,b = s.split('=')
				a += ' ='
			else:
				b = b.strip()
				if b.startswith('return '):
					b = b[len('return '):]
					draw_type = 'up-arrow-callout'
					color = 'BLACK'
			fodgy += 1.5
			x = fodgx + (indent*2)
			fodg.append(
				'<draw:custom-shape draw:text-style-name="%s" xml:id="id%s" draw:id="id%s" draw:layer="layout" svg:width="14.224cm" svg:height="8.001cm" svg:x="%scm" svg:y="%scm">' %(color, fid, fid, x, fodgy)
			)
			fodg.append('<text:p><text:span text:style-name="DEF">%s</text:span></text:p>' %escape(b))
			#fodg.append('<draw:enhanced-geometry svg:viewBox="0 0 21600 21600" draw:type="rectangle" draw:enhanced-path="M 0 0 L 21600 0 21600 21600 0 21600 0 0 Z N"/>')
			fodg.append('<draw:enhanced-geometry draw:type="%s"/>' %draw_type)
			fodg.append('</draw:custom-shape>')
			fodg.extend([
				'<draw:connector ',
				'	draw:style-name="gr11" draw:text-style-name="P8" draw:layer="layout" svg:x1="%scm" svg:y1="%scm" ' %(x, fodgy-1),
				'	svg:x2="9.509cm" svg:y2="9.509cm" draw:start-shape="id%s" draw:start-glue-point="%s" ' %(fid-1, 2),  ## 2 is bottom, 3 is left, 1 is right
				'	draw:end-shape="id%s" draw:end-glue-point="%s" svg:d="M3286 9001v573h3655v-566h2568v501" svg:viewBox="0 0 6224 574">' %(fid, 4),  ## 4 is top
				'<text:p/>',
				'</draw:connector>',
			])
			if a:
				#fid += 1
				fodg.append(
					'<draw:custom-shape draw:text-style-name="YELLOW" xml:id="sub-id%s" draw:id="sub-id%s" draw:layer="layout" svg:width="14.224cm" svg:height="8.001cm" svg:x="%scm" svg:y="%scm">' %(fid, fid, x-5, fodgy-1)
				)
				fodg.append('<text:p><text:span text:style-name="DEF">%s</text:span></text:p>' %escape(a))
				#fodg.append('<draw:enhanced-geometry svg:viewBox="0 0 21600 21600" draw:type="rectangle" draw:enhanced-path="M 0 0 L 21600 0 21600 21600 0 21600 0 0 Z N"/>')
				if u'🠊' in a:
					fodg.append('<draw:enhanced-geometry draw:type="notched-right-arrow"/>')
				elif '[' in a:
					fodg.append('<draw:enhanced-geometry draw:type="right-arrow-callout"/>')
				elif '.' in a:
					fodg.append('<draw:enhanced-geometry draw:type="pentagon-right"/>')
				else:
					fodg.append('<draw:enhanced-geometry draw:type="right-arrow"/>')
				fodg.append('</draw:custom-shape>')
				fodg.extend([
					'<draw:connector ',
					'	draw:style-name="gr11" draw:text-style-name="P8" draw:layer="layout" svg:x1="%scm" svg:y1="%scm" ' %(x, fodgy-1),
					'	svg:x2="9.509cm" svg:y2="9.509cm" draw:start-shape="id%s" draw:start-glue-point="%s" ' %(fid, 3),  ## 2 is bottom, 3 is left, 1 is right
					'	draw:end-shape="sub-id%s" draw:end-glue-point="%s" svg:d="M3286 9001v573h3655v-566h2568v501" svg:viewBox="0 0 6224 574">' %(fid, 1),  ## 4 is top
					'<text:p/>',
					'</draw:connector>',
				])
				fodgy += 1.5
			if s.startswith(('if ', 'elif ', 'else', 'for ', 'while ')) and s.endswith(":"):
				#fodgx += 0.5
				pass

	if previ >= 2:
		out.append('}' * (previ-1) )
	#elif autofunc:
	#	out.append('} // autobrace: %s' %previ)


	if virt_func_dispatch:
		for vclass in virt_func_dispatch:
			for vmeth in virt_func_dispatch[vclass]:
				vinfo = virt_func_dispatch[vclass][vmeth]
				vinfo['code'].extend([
					'		default:',
					'			std::cout << "virtual method dispatch error, class-id = " << this->pointer.classid << std::endl;',
					'			throw "virtual method dispatch error";',
					'	}; // end of switch',
					'}  // end of virtual method dispatch'				
				])
				out.extend( vinfo['code'] )

	if mods and user_pythonic:
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
		elif functions:
			if 'tp_import' in functions:
				if 'scramble' in functions['tp_import']:
					tp_import = functions['tp_import']['scramble']
			if 'tp_set' in functions:
				if 'scramble' in functions['tp_set']:
					tp_set = functions['tp_set']['scramble']
			if 'tp_function' in functions:
				if 'scramble' in functions['tp_function']:
					tp_function = functions['tp_function']['scramble']

		for i,modname in enumerate(mods):
			m = 'mod%s' %i
			out.append('	tp_obj %s = %s(tp, tp_string_atom(tp, "%s"),tp_None, tp_string_atom(tp, "<c++>"));' %(m, tp_import, modname))
			#out.append('	tp_obj %s = %s(tp, "%s", "<c++>");' %(m, tp_import, modname))
			for func in mods[modname]:
				if type(func) is dict:
					scram = func['scram']
					unscram = func['unscram']
					out.append('	%s(tp, %s, tp_string_atom(tp, "%s"), %s(tp, %s));' %(tp_set, m, unscram, tp_function, scram))
				elif type(func) is list:
					assert len(func)==2
					out.append('	%s(tp, %s, "%s", %s(tp, %s));' %(tp_set, m,func[0], tp_function, func[1]))
				
				else:
					out.append('	%s(tp, %s, tp_string_atom(tp, "%s"), %s(tp, %s));' %(tp_set, m,func, tp_function, func))

		out.append('}')


	if unreal_plugin_cpp:
		unreal_plugin_cpp.extend(out)
		unreal_plugin_cpp.append('IMPLEMENT_MODULE( F%s, %s )' %(unreal_plugin_name, unreal_plugin_name))
		cpp = {
			'lib': '\n'.join(unreal_plugin_lib),
			'iface' : '\n'.join(unreal_plugin_iface),
			'impl' : '\n'.join(unreal_plugin_cpp),
			'blueprints' : None
		}
		if unreal_blueprints:
			bp_out = []
			for bp_name in unreal_blueprints:
				bp_src = unreal_blueprints[bp_name]
				if bp_name.startswith( ('"', "'") ):
					bp_name = bp_name[1:-1]
				bp_out.append('with unreal.%s:' %bp_name)
				bp_out.extend(bp_src)
			bp_out = '\n'.join(bp_out)
			ugen = unrealgen.UnrealGen(bp_out)
			ugen.visit(ast.parse(bp_out))
			ugen_script = ugen.get_gen_script()
			#raise RuntimeError(ugen_script)
			cpp['blueprints'] = ugen_script

	else:
		cpp = '\n'.join(out)


	if '--inspect-pythonic++' in sys.argv:
		raise RuntimeError(cpp)

	if 'classes' in info:
		info['classes'].update( classes )

	if fodg:
		fodg.extend([
			#'</draw:custom-shape>'
			'			</draw:page>',
			'		</office:drawing>',
			'	</office:body>',
			'</office:document>',
		])

	return cpp

def metapy2tinypypp( source ):
	shared = []
	right_side = []
	thread_local = []
	thread = None
	cpy = None
	cpp = []
	aot = []
	js = []
	in_cpp = False
	in_js = False
	in_aot = False
	aot_all = False
	append_next_blank_hack = None
	
	if '--aot-all' in sys.argv:
		in_aot = True
		aot_all = True
		
	#if tpy_modules_aot:
	#	for aotmod in tpy_modules_aot:
	#		aot.extend(tpy_modules_aot[aotmod])

	for ln in source.splitlines():
		if u'┃' in ln:
			assert ln.count(u'┃')==1
			a,b = ln.split(u'┃')
			shared.append(a)
			right_side.append(b)
		elif ln.startswith('with javascript:'):
			if js:
				raise SyntaxError('with javascript: can only be used once')
			in_js = True
		elif ln.startswith('with c++:'):
			cpp = []
			in_cpp = True
		elif ln.lower().startswith( ('# aot begin', '#aot begin') ):
			in_aot = True
			aot_all = False
		elif ln.lower().startswith( ('# aot end', '#aot end') ):
			in_aot = False
		elif ln.lower().startswith( 'main()' ) and aot_all:
			shared.append('aotpy_main__()')
		elif ln.startswith('with python:'):
			cpy = []
		elif ln.startswith('with thread:'):
			thread = []
			thread_local.append(thread)
		elif in_js:
			if not ln.strip():
				in_js = False
			else:
				js.append(ln)
		elif in_aot:
			if ln.strip():
				if ln.lower().startswith( ('# aot export', '#aot export') ):
					aot.append('@module(__aot_builtin_module__)')
				elif ln.startswith( 'def main(' ):
					assert aot_all
					aot.append('@module(__aot_builtin_module__)')
					aot.append('\tdef aotpy_main__():')
					append_next_blank_hack = '\treturn None'
				elif ln.strip().startswith("print('") and ln.strip().endswith("')"):
					aot.append( '\t' + ln.replace("print('", 'print("')[:-2]+'")' )
				elif ln.strip() == 'import sdl':
					aot.append('\t' + "sdl = sdlwrapper()")
				else:
					aot.append('\t' + ln.split('#')[0])
			elif append_next_blank_hack:
				aot.append( '\t' + append_next_blank_hack )
				append_next_blank_hack = None

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

	if aot:
		shared.insert(0, 'from __aot_builtin_module__ import *')
		if '--debug' in sys.argv:
			print('============ AOT compile to C++ ==============')
			print('\n'.join(aot))
			print('----------------------------------------------')
	else:
		has_aot_mods = False
		for ln in shared:
			for part in ln.split():
				if 'world(' in part:
					has_aot_mods = True
					break
		if has_aot_mods:
			shared.insert(0, 'from __aot_builtin_module__ import *')

	if '--wasm' in sys.argv:
		## special case to transform the first `while True: myfunc()` into a call to emscripten_set_main_loop
		## http://main.lv/writeup/web_assembly_sdl_example.md
		newshared = []
		hits = 0
		for ln in shared:
			s = ln.strip()
			if s.startswith('while True:') and s.count('(')==1 and s.count(')'):
				assert s.endswith(')')
				assert hits == 0
				#TODO also assert that the function takes no args
				func_name = s.split(':')[-1].split('(')[0].strip()
				ln = '\t' * ln.split(':')[0].count('\t')
				ln += 'em_set_main( %s )' %func_name
				hits += 1
			newshared.append(ln)
		shared = newshared

	print('============compile to bytecode ==============')
	print('\n'.join(shared))
	print('----------------------------------------------')
	#raise RuntimeError('\n'.join(shared))

	if aot and len(shared)==1:
		raise SyntaxError('bytecode is blank, did you forget to define and call `main()` at the end of the script?')

	scripts = []
	if len(thread_local):
		for thread_code in thread_local:
			script = '\n'.join(shared)
			script += '\n'
			script += '\n'.join(thread_code)
			scripts.append(script)
	else:
		if js:
			info = {'js_funcs':{}, 'js_header':[]}
			js = pythonicpp(js, info=info, mode='js')

			if info['js_funcs']:
				new_shared = []
				for ln in shared:
					for jsfunc in info['js_funcs']:
						jsig = info['js_funcs'][jsfunc]
						if jsfunc+'(' in ln:
							prevchar = ln[ ln.index(jsfunc)-1 ]
							if prevchar in '\t +=-*/[]();,?':
								if len(jsig['args']):
									rargs = ['%s'] * len(jsig['args'])
									rargs = ','.join(rargs)
									## note: tiny_list params no longer support keyword args
									#ln = ln.replace(jsfunc+'(', 'javascript("'+jsfunc+'('+rargs+')" % (') + ', returns="%s")'%jsig['returns']
									ln = ln.replace(jsfunc+'(', 'javascript("'+jsfunc+'('+rargs+')" % (') + ', "%s")'%jsig['returns']
								else:
									## note: tiny_list params no longer support keyword args
									#ln = ln.replace(jsfunc+'()', 'javascript("'+jsfunc+'()"') + ', returns="%s")'%jsig['returns']
									ln = ln.replace(jsfunc+'()', 'javascript("'+jsfunc+'()"') + ', "%s")'%jsig['returns']
							else:
								raise SyntaxError('unable to auto-wrap javascript function')
							break
					new_shared.append(ln)
				shared = new_shared
				shared = ['evaljs("""', js, '""")'] + shared

				if cpp:
					new_cpp = []
					for ln in cpp:
						for jsfunc in info['js_funcs']:
							jsig = info['js_funcs'][jsfunc]
							if jsfunc+'(' in ln:
								prevchar = ln[ ln.index(jsfunc)-1 ]
								if prevchar in '\t +=-*/[]();,?':
									rargs = ['$%s' % i for i in range(len(jsig['args']))]
									rargs = ','.join(rargs)
									if jsig['returns'] == 'void':
										ln = ln.replace(jsfunc+'(', 'EM_ASM({'+jsfunc+'('+rargs+')}, ')
									elif jsig['returns'] == 'int':
										ln = ln.replace(jsfunc+'(', 'EM_ASM_INT({return '+jsfunc+'('+rargs+')}, ')
									elif jsig['returns'] in ('float', 'double'):
										ln = ln.replace(jsfunc+'(', 'EM_ASM_DOUBLE({return '+jsfunc+'('+rargs+')}, ')
									else:
										raise SyntaxError('unable to auto-wrap javascript function - unsupported return type: %s' %jsig['returns'])

								else:
									raise SyntaxError('unable to auto-wrap javascript function')
								break
						new_cpp.append(ln)
					cpp = new_cpp
			else:
				shared = ['evaljs("""', js, '""")'] + shared

			if info['js_header']:
				##shared = ['evaljs("""'] + info['js_header'] + ['""")'] + shared  ## makes bytecode too big
				dat = '\n'.join(info['js_header'])
				open('/tmp/tpython_preload_libs.js', 'wb').write(dat.encode('utf-8'))

		script = '\n'.join(shared)
		scripts.append(script)
		
	cpp = '\n'.join(cpp + aot)
	return scripts, cpp

def walk_path(path, res):
	for file in os.listdir(path):
		if file.endswith(('.aot.pyc++', '.aot.pyh')):
			res.insert(0, [path,file])
		elif file.endswith(('.pyc++', '.pyh')):
			res.append([path,file])
		elif os.path.isdir(os.path.join(path,file)):
			if file == 'blendot':
				if '--blendot' in sys.argv:
					walk_path( os.path.join(path,file), res)
			else:
				walk_path( os.path.join(path,file), res)

def pythonicpp_translate( path, file=None, secure=False, secure_binary=False, mangle_map=None, obfuscate_map=None, unreal=False, unreal_project=None, vis=None, vis_cursor=None ):
	if file:
		print('	translate file: ', file)
	else:
		print('	translate path: ', path)
	new_obfuscate = {}
	info = {'classes':{}, 'functions':{}, 'obfuscations':new_obfuscate}
	files = []
	if file:
		files.append([path,file])
	else:
		walk_path(path, files)

	unreal_plugin_name=None
	if unreal:
		unreal_plugin_name = path.split('/')[-1].split('.')[0]


	if secure:
		## first pass gather function info
		for path, file in files:
			if file.endswith( '.pyc++' ):
				print(file)
				cpp = pythonicpp( open(os.path.join(path,file),'rb').read().decode('utf-8'), header="/*generated from: %s*/" %file, info=info )
			elif file.endswith( '.pyh' ):
				print(file)
				cpp = pythonicpp(
					open(os.path.join(path,file),'rb').read().decode('utf-8'), 
					header="/*generated from: %s*/" %file, info=info,
					swap_self_to_this=file=='__user_pythonic__.pyh'
				)

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
		print('	' + file)
		#if not unreal_plugin_name:
		if path.endswith( ('.unreal', '.unreal/') ):
			unreal_plugin_name = os.path.split(path.split('.')[0])[-1]

		if file.endswith( '.pyc++' ):
			fodg = []
			cpp = pythonicpp(
				open(os.path.join(path,file),'rb').read().decode('utf-8'), 
				header="/*generated from: %s*/" %file, 
				info=info, 
				binary_scramble=secure_binary, 
				mangle_map=mangle_map, 
				fodg=fodg, 
				unreal_plugin_name=unreal_plugin_name,
				file_name=os.path.join(path,file),
				vis_cursor=vis_cursor
			)

			if unreal or type(cpp) is dict:
				if file == 'Plugin.pyc++':
					assert type(cpp) is dict
					if 'lib' in cpp and cpp['lib']:
						print('	saving: ', 'tinypy/__user_pythonic__.gen.h')
						open('tinypy/__user_pythonic__.gen.h','wb').write(cpp['lib'].encode('utf-8'))

					if cpp['blueprints']:
						upath = os.path.join(unreal_project, 'Content/Scripts/' )
						uname = 'gen_' + unreal_plugin_name + '.py'
						if not os.path.isdir(upath):
							os.makedirs(upath)
						print('	saving: ', os.path.join(upath, uname ))
						open(os.path.join(upath, uname ),'wb').write(cpp['blueprints'].encode('utf-8'))
						print('the blueprint generator requires https://github.com/20tab/UnrealEnginePython')
						print('you must install the plugin and enable it for your Unreal project')
					else:
						print('Plugin.pyc++ contains no blueprints')

					uheader = cpp['iface']
					cpp = cpp['impl']


					upath = os.path.join(unreal_project, 'Plugins/%s/Source/%s/Public/' %(unreal_plugin_name, unreal_plugin_name) )
					uname = 'I' + unreal_plugin_name + '.h'
					if not os.path.isdir(upath):
						os.makedirs(upath)
					print('	saving: ', os.path.join(upath, uname ))
					open(os.path.join(upath, uname ),'wb').write(uheader.encode('utf-8'))

					upath = os.path.join(unreal_project, 'Plugins/%s/Source/%s/Private/' %(unreal_plugin_name, unreal_plugin_name) )
					uname = unreal_plugin_name + '.cpp'

				else:
					upath = os.path.join(unreal_project, 'Plugins/%s/Source/%s/Private/' %(unreal_plugin_name, unreal_plugin_name) )
					uname = file.replace('.pyc++', '.cpp')
					cpp = ('#include "%s"\n' % file.replace('.pyc++', '.h')) + cpp

				if not os.path.isdir(upath):
					os.makedirs(upath)

				print('	saving: ', os.path.join(upath, uname ))
				open(os.path.join(upath, uname ),'wb').write(cpp.encode('utf-8'))

			else:
				print('	saving: ', os.path.join(path,file.replace('.pyc++', '.gen.cpp')))
				open(os.path.join(path, file.replace('.pyc++', '.gen.cpp') ),'wb').write(cpp.encode('utf-8'))

			if fodg:
				fodg = '\n'.join(fodg)
				fodg_path = os.path.join(path, file.replace('.pyc++', '.pyc++.fodg') )
				open(fodg_path,'wb').write(fodg.encode('utf-8'))
				if vis:
					subprocess.check_call(['soffice', '--headless', '--convert-to', 'png:draw_png_Export', fodg_path], cwd='/tmp')
					png_path = os.path.join('/tmp', file.replace('.pyc++', '.pyc++.png') )
					subprocess.check_call(['convert', png_path, '-crop', '800x200x0x0', '+repage', vis])
					subprocess.check_call(['mv', '-v', vis.replace('.png', '-0.png'), vis])

		elif file.endswith( '.pyh' ):
			cpp = pythonicpp( 
				open(os.path.join(path,file),'rb').read().decode('utf-8'), 
				header="/*generated from: %s*/" %file, info=info, 
				binary_scramble=secure_binary, mangle_map=mangle_map,
				swap_self_to_this=file=='__user_pythonic__.pyh',
				file_name = os.path.join(path,file)
			)
			if cpp is None:
				assert file.endswith('.aot.pyh')
			elif unreal:
				assert unreal_plugin_name
				if file == 'PrivatePCH.pyh':
					upath = os.path.join(unreal_project, 'Plugins/%s/Source/%s/Private/' %(unreal_plugin_name, unreal_plugin_name) )
					uname = unreal_plugin_name + 'PrivatePCH.h'
				else:
					upath = os.path.join(unreal_project, 'Plugins/%s/Source/%s/Classes/' %(unreal_plugin_name, unreal_plugin_name) )
					uname = file.replace('.pyh', '.h')
					cpp = '\n'.join([
						'#include "%sPrivatePCH.h"' % unreal_plugin_name,
						## generated by the unreal build tool
						'#include "%s.generated.h"' % file.split('.')[0],
						cpp
					])

				if not os.path.isdir(upath):
					os.makedirs(upath)

				print('	saving: ', os.path.join(upath, uname ))

				open(os.path.join(upath, uname ),'wb').write(cpp.encode('utf-8'))

			else:
				print('	saving: ', os.path.join(path,file.replace('.pyh', '.gen.h')))
				open(os.path.join(path, file.replace('.pyh', '.gen.h') ),'wb').write(cpp.encode('utf-8'))


	if unreal:
		uplugin = UPLUGIN_TEMPLATE %(
			unreal_plugin_name, 
			'tpython', 
			'https://gitlab.com/hartsantler/tpythonpp',
			UNREAL_VER,
			'tpython plugin',
			'Examples',
			'true',
			unreal_plugin_name,
			'Developer',
			'PreDefault'
		)
		upath = os.path.join(unreal_project, 'Plugins/%s/' %unreal_plugin_name )
		if not os.path.isdir(upath):
			os.makedirs(upath)
		open(os.path.join(upath, '%s.uplugin' %unreal_plugin_name ),'wb').write(uplugin.encode('utf-8'))


		buildcs = UNREAL_BUILD_TEMPLATE %tuple( [unreal_plugin_name]*7 )
		upath = os.path.join(unreal_project, 'Plugins/%s/Source/%s/' %(unreal_plugin_name, unreal_plugin_name) )
		if not os.path.isdir(upath):
			os.makedirs(upath)
		open(os.path.join(upath, '%s.Build.cs' %unreal_plugin_name ),'wb').write(buildcs.encode('utf-8'))


	return info

def main():
	print('pyc++ compilier and tpythonpp bytecode translator')
	global UNREAL_VER
	input_file = None
	exargs = []
	pythonicpp_paths = []
	mangle_map = []
	obfuscate_map = {}
	unreal_mode = False
	unreal_plugin = None
	unreal_project = os.path.expanduser('~/Documents/Unreal Projects/TPythonPluginTest')
	vis_output = None
	vis_cursor = None
	mode = 'linux'

	for arg in sys.argv[1:]:
		if arg.endswith( '.py' ):
			input_file = arg
		elif arg.endswith( ('.pyc++', '.pyh') ):
			input_file = arg
		elif arg.startswith('--'):
			if arg == '--unreal':
				unreal_mode = True
			elif arg.startswith('--unreal-version='):
				UNREAL_VER = arg.split('=')[-1]
			elif arg == '--windows':
				mode = 'windows'
			elif arg.startswith('--vis-cursor'):  ## line-number : character offset
				vis_cursor = arg.split('=')[-1]
				cx,cy = vis_cursor.split('/')
				cx = int(cx.strip())
				cy = int(cy.strip())
				vis_cursor = (cx,cy)
			elif arg.startswith('--vis'):
				vis_output = arg.split('=')[-1]
				if vis_output.startswith('"'):
					vis_output = vis_output[1:-1]
			else:
				exargs.append(arg)
		elif os.path.isdir(arg):
			if unreal_mode:
				if arg.endswith( ('.unreal', '.unreal/') ):
					unreal_plugin = arg
					pythonicpp_paths.append( arg )
				else:
					unreal_project = arg
			else:
				pythonicpp_paths.append( arg )
		elif arg.startswith('[') and arg.endswith(']'):
			mangle_map = json.loads(arg)
		elif arg.endswith('.json'):
			obfuscate_map = json.loads(open(arg,'rb').read())

	if unreal_mode and mode=='windows':
		global UNREAL_BUILD_TEMPLATE
		assert '"libtpython++.so"' in UNREAL_BUILD_TEMPLATE
		UNREAL_BUILD_TEMPLATE = UNREAL_BUILD_TEMPLATE.replace('"libtpython++.so"', '"libtpython++.dll"')

	if input_file:
		cpp = None
		scripts = []
		path, name = os.path.split(input_file)
		thisdir = os.path.split(os.path.abspath(__file__))[0]
		## fixes relative paths
		if thisdir.endswith('tpythonpp') and input_file.startswith('tpythonpp/'):
			input_file = input_file[ len('tpythonpp/') : ]
		input_file = os.path.join(thisdir, input_file)
		assert os.path.isfile(input_file)
		if input_file.endswith( '.py' ):
			## user level
			scripts, cpp = metapy2tinypypp( open(input_file, 'rb').read().decode('utf-8') )
		else:
			## low level
			path, name = os.path.split(input_file)
			if input_file.endswith('.pyh'):
				print('translate phy file: ', input_file)
			else:
				print('translate pyc++ file: ', input_file)

			info = pythonicpp_translate(
				path, 
				file=name,
				secure='--secure' in sys.argv, 
				secure_binary='--secure-binary' in sys.argv, 
				mangle_map=mangle_map,
				obfuscate_map=obfuscate_map,
				unreal=unreal_mode,
				unreal_project = unreal_project,
				vis=vis_output,
				vis_cursor=vis_cursor
			)

		if cpp:
			open('./tinypy/__user_pythonic__.pyh', 'wb').write(cpp.encode('utf-8'))

		if len(scripts) == 1:
			source = scripts[0]
			tempf = '/tmp/%s_main.py'%name
			if '--debug' in sys.argv:
				print(source)

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
				obfuscate_map=obfuscate_map,
				unreal=unreal_mode,
				unreal_project = unreal_project
			)
			if not obfuscate_map:
				p = path.split('/')[-1]
				open('/tmp/%s.json' %p, 'wb').write( json.dumps(info['obfuscations']).encode('utf-8') )

		## tpy_modules_aot should have been cleared if there was user pythonic,
		## so in case the user has no pythonic code and modules are used, still need to save the AOT modules here
		if tpy_modules_aot:
			aotsrc = []
			for aotmod in tpy_modules_aot:
				aotsrc.extend( tpy_modules_aot[aotmod] )
				
			print('\n'.join(aotsrc))
			print('=====================================')
			cpp = pythonicpp( [], file_name='__user_pythonic__.pyh', swap_self_to_this=True)
			print(cpp)
			print('	saving: ', os.path.join(path,'__user_pythonic__.gen.h') )
			open( os.path.join(path,'__user_pythonic__.gen.h'), 'wb').write(cpp.encode('utf-8'))



main()




