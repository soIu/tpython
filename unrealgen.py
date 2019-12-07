import ast
import sys

UNREAL_MODULE_TEMPLATE = '''
#pragma once
#include "ModuleManager.h"
#include "Runtime/UMG/Public/UMG.h"
#include "Runtime/UMG/Public/UMGStyle.h"
#include "Runtime/UMG/Public/Slate/SObjectWidget.h"
#include "Runtime/UMG/Public/IUMGModule.h"
#include "Runtime/UMG/Public/Blueprint/UserWidget.h"
#include "AIController.h"
#include "Components/AudioComponent.h"
#include "AudioDecompress.h"
#include "AudioDevice.h"
#include "ActiveSound.h"
#include "Audio.h"
#include "Developer/TargetPlatform/Public/Interfaces/IAudioFormat.h"
#include "VorbisAudioInfo.h"
#include "GameFramework/Actor.h"

'''

UnPyBlueprint_HEADER = '''
import unreal_engine as _ue
from unreal_engine.classes import Actor as _actor
from unreal_engine.classes import K2Node_MakeArray as _makearr
from unreal_engine.classes import K2Node_MathExpression as _exp
from unreal_engine.classes import K2Node_Switch as _switch
from unreal_engine.classes import K2Node_IfThenElse as _ifelse
from unreal_engine.classes import K2Node_ExecutionSequence as _seq
from unreal_engine.classes import KismetSystemLibrary as _sys
from unreal_engine.classes import KismetMathLibrary as _math
from unreal_engine.structs import EdGraphPinType
from unreal_engine.enums import EEdGraphPinDirection
from unreal_engine.classes import K2Node_MacroInstance
from unreal_engine.structs import GraphReference
_print = _sys.PrintString
_makestr = _sys.MakeLiteralString
_makeint = _sys.MakeLiteralInt
_makefloat = _sys.MakeLiteralFloat
'''

def is_print(node):
	#if isinstance(node, ast.Print):  ## python2
	#	return True
	if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id=='print':
		return True

	return False

class CLikeLanguage:
	def visit_Str(self, node):
		return '"%s"' % node.s
	def visit_Name(self, node):
		return node.id

	def visit_Not(self, node):
		return '!'

	def visit_USub(self, node):
		return '-'
		
	def visit_And(self, node):
		return ' && '

	def visit_Or(self, node):
		return ' || '


	def visit_Eq(self, node):
		return '=='

	def visit_NotEq(self, node):
		return '!='

	def visit_Num(self, node):
		return str(node.n)

	def visit_Mult(self, node):
		return '*'

	def visit_Add(self, node):
		return '+'

	def visit_Sub(self, node):
		return '-'

	def visit_Div(self, node):
		return '/'

	def visit_Mod(self, node):
		return '%'

	def visit_Lt(self, node):
		return '<'

	def visit_Gt(self, node):
		return '>'

	def visit_GtE(self, node):
		return '>='

	def visit_LtE(self, node):
		return '<='

	def visit_LShift(self, node):
		return '<<'
	def visit_RShift(self, node):
		return '>>'
	def visit_BitXor(self, node):
		return '^'
	def visit_BitOr(self, node):
		return '|'
	def visit_BitAnd(self, node):
		return '&'

class UnrealGen(ast.NodeVisitor, CLikeLanguage):

	def __init__(self, source_code):
		self._line = None
		self._line_number = 0
		self._stack = []        ## current path to the root
		self._source = source_code.splitlines()
		self.blueprint = ''
		self.blueprint_graph = []
		self.blueprint_name = 'unnamed_blueprint'
		self.graphs = []

	def get_gen_script(self):
		return '\n'.join( [UnPyBlueprint_HEADER]+self.graphs )

	def visit(self, node):
		"""Visit a node."""
		## modified code of visit() method from Python 2.7 stdlib
		self._stack.append(node)
		if hasattr(node, 'lineno'):
			lineno = node.lineno
			if node.lineno < len(self._source):
				src = self._source[ node.lineno ]
				self._line_number = node.lineno
				self._line = src

		method = 'visit_' + node.__class__.__name__
		visitor = getattr(self, method, self.generic_visit)
		res = visitor(node)
		self._stack.pop()
		if res is None:
			if isinstance(node, (ast.Load, ast.Module)):
				return res
			print(dir(node))
			raise RuntimeError('TODO Node Type: %s' %self.format_error(node))
		return res


	def format_error(self, node):
		lines = []
		if self._line_number > 0:
			n = self._line_number-1
			lines.append( '%s:	%s '%(n, self._source[n]) )
		lines.append( '%s:	%s '%(self._line_number, self._source[self._line_number]) )

		for i in range(1,2):
			if self._line_number+i < len(self._source):
				n = self._line_number + i
				lines.append( '%s:	%s '%(n, self._source[n]) )

		msg = 'line %s\n%s\n%s\n' %(self._line_number, '\n'.join(lines), node)
		msg += 'Depth Stack:\n'
		for l, n in enumerate(self._stack):
			#msg += str(dir(n))
			if isinstance(n, ast.Module):
				pass
			else:
				msg += '%s%s line:%s col:%s\n' % (' '*(l+1)*2, n.__class__.__name__, n.lineno-1, n.col_offset)
		return msg


	def visit_Compare(self, node):
		comp = ['(']
		left = self.visit(node.left)
		if isinstance(node.left, ast.BinOp):
			comp.extend( ['(', self.visit(node.left), ')'] )
		else:
			comp.append( self.visit(node.left) )

		for i in range( len(node.ops) ):
			op = node.ops[i]
			rator = self.visit(node.comparators[i])

			if isinstance(op, ast.In) or isinstance(op, ast.NotIn):
				if comp[-1]==left:
					comp.pop()
				else:
					comp.append(' && ')

				comp.append('(std::find(%s->begin(), %s->end(), %s) != %s->end())' %(rator, rator, left, rator))
				##slower than std::find ##
				#comp.append('(std::count(%s->begin(), %s->end(), %s) >= 1)' %(rator, rator, left))

			else:
				comp.append( self.visit(op) )

				if isinstance(node.comparators[i], ast.BinOp):
					comp.append('(')
					comp.append( self.visit(node.comparators[i]) )
					comp.append(')')
				else:
					comp.append( self.visit(node.comparators[i]) )

		comp.append( ')' )
		print(comp)
		return ' '.join( comp )

	def visit_With(self, node):
		#print(node.items)
		#print(dir(node.items[0]))
		#print(dir(node))
		assert len(node.items)==1
		node.context_expr = node.items[0].context_expr  ## Python3 fix
		if isinstance( node.context_expr, ast.Attribute ): #and self.visit(node.context_expr)=='unreal.blueprint':
			self.blueprint_name = node.context_expr.attr
			#compiled_loops = []
			graph = [
				'_bp = _ue.create_blueprint(_actor, "/Game/%s")' %self.blueprint_name,
				'_g = _bp.UberGraphPages[0]',
				'_x, _y = _g.graph_get_good_place_for_new_node()',
				'print("	make main node for: %s")' %self.blueprint_name,
				'_mainnode = _g.graph_add_node(_seq, _x, _y)',
			]
			then = 0
			vars = {}
			for b in node.body:
				if isinstance(b, ast.Expr):
					b = b.value
				if then >= 2:
					graph.append('_mainnode.node_create_pin(EEdGraphPinDirection.EGPD_Output, EdGraphPinType(PinCategory="exec"), "Then_%s")' %then)
				#############################

				if isinstance(b, ast.For):  ## TODO check for break
					'Exec', 'Array', 'LoopBody', 'Array Element', 'Array Index', 'Completed'
					graph.append('_x, _y = _g.graph_get_good_place_for_new_node()')
					graph.append('fnode = _g.graph_add_node(K2Node_MacroInstance, _x, _y)')
					graph.append('fnode.MacroGraphReference = GraphReference(MacroGraph=_ue.find_object("ForEachLoop"))')
					graph.append('fnode.node_allocate_default_pins()')
					graph.append('_ue.blueprint_mark_as_structurally_modified(_bp)')
					graph.append('fnode.node_find_pin("Array").make_link_to(%s_outpin)' %b.iter.id)

					graph.append('_forbody = _g.graph_add_node(_seq, _x+150, _y+100)')
					graph.append('fnode.node_find_pin("LoopBody").make_link_to(_forbody.node_find_pin("execute"))')

					vname = b.target.id
					graph.append('_ue.blueprint_add_member_variable(_bp, "%s", "array")' %vname)
					graph.append('set_%s = _g.graph_add_node_variable_set("%s", None, -500, _y)' %(vname,vname))
					graph.append('fnode.node_find_pin("Array Element").make_link_to(set_%s.node_find_pin("%s"))' %(vname,vname))
					graph.append('%s_outpin = set_%s.node_find_pin("Output_Get")' %(vname,vname))

					for i,c in enumerate( b.body ):
						if i>=2:
							graph.append('_forbody.node_create_pin(EEdGraphPinDirection.EGPD_Output, EdGraphPinType(PinCategory="exec"), "Then_%s")' %i)
						if is_print(c):
							graph.append('print("new for print")')
							graph.append('_printnode = _g.graph_add_node_call_function(_print, _x+400, _y+150+%s)' %str(i*100))
							graph.append('_forbody.node_find_pin("Then_%s").make_link_to(_printnode.node_find_pin("execute"))' %i)
							for item in c.values:
								if isinstance(item, ast.Name):
									graph.append('_printnode.node_find_pin("InString").make_link_to(%s_outpin)' %item.id)


					#forname = 
					#forcode = UnPyRuntime_ForEachArray %(forname, arrname, arrtype, itername, forbody)
					#raise RuntimeError( '\n'.join(graph) )
				elif isinstance(b, ast.Call) and not (isinstance(b.func, ast.Name) and b.func.id == 'print'):
					#cname, fname = self.visit(b.func).split('.__doublecolon__.')
					cname = fname = b.func.id
					print(b.func)
					print(fname)
					graph.append('from unreal_engine.classes import %s as T' %cname)
					graph.append('call_%s = _g.graph_add_node_call_function(T.%s, _x, _y)' %(fname, fname))
					#graph.append('call_%s.node_find_pin("ReturnValue").make_link_to(set_%s.node_find_pin("%s"))' %(vname, vname, vname))
					graph.append('_mainnode.node_find_pin("Then_%s").make_link_to(call_%s.node_find_pin("execute"))' %(i, fname))
					for kw in b.keywords:
						graph.append('pin = call_%s.node_find_pin("%s")' %(fname, kw.arg))
						graph.append('pin.make_link_to(%s_outpin)' %kw.value.id)
				elif isinstance(b, ast.Assign):
					vname = b.targets[0].id
					graph.append('_y = %s' %(len(vars.keys())*200) )
					if isinstance(b.value, ast.Str):
						vars[vname] = b.value.s
						graph.append('_ue.blueprint_add_member_variable(_bp, "%s", "string")' %vname)
					else:
						vars[vname] = 'TArray'
						graph.append('_ue.blueprint_add_member_variable(_bp, "%s", "wildcard")' %vname)

					graph.append('set_%s = _g.graph_add_node_variable_set("%s", None, -500, _y)' %(vname,vname))
					graph.append('%s_outpin = set_%s.node_find_pin("Output_Get")' %(vname,vname))

					if isinstance(b.value, ast.Str):
						graph.append('make_%s = _g.graph_add_node_call_function(_makestr, -800, _y)' %vname)
						graph.append('make_%s.node_find_pin("ReturnValue").make_link_to(set_%s.node_find_pin("%s"))' %(vname, vname, vname))
						graph.append('make_%s.node_find_pin("Value").default_value = "%s"' %(vname, b.value.s))
					else:
						graph.append('make_%s = _g.graph_add_node(_makearr, -800, _y)' %vname)
						graph.append('make_%s.node_find_pin("Array").make_link_to(set_%s.node_find_pin("%s"))' %(vname, vname, vname))
						if len(b.value.args[0].elts):
							for i,elt in enumerate(b.value.args):
								if isinstance(elt, ast.Num):
									graph.append('valnode = _g.graph_add_node(_makeint, -900, _y)')
									graph.append('make_%s.node_find_pin("[%s]").make_link_to(valnode.node_find_pin("ReturnValue"))' %(vname,i) )
									graph.append('valnode.node_find_pin("Value").default_value = %s' %(vname, b.value.args[0].elts[0].n) )

					continue

				elif isinstance(b, ast.If):
					graph.append('print("	new if")')
					graph.append('_x, _y = _g.graph_get_good_place_for_new_node()')
					graph.append('_ifnode = _g.graph_add_node(_ifelse, _x, _y)')
					graph.append('_mainnode.node_find_pin("Then_%s").make_link_to(_ifnode.node_find_pin("execute"))' %then)
					graph.append('_iftest = _g.graph_add_node(_exp, _x-300, _y)')
					#graph.append('_iftest.set_name("%s")' %self.visit(b.test))
					expr = self.visit(b.test)
					graph.append("_iftest.Expression = '''%s'''" %expr)
					graph.append('_iftest.node_reconstruct()')
					graph.append('_iftest.node_find_pin("ReturnValue").make_link_to(_ifnode.node_find_pin("Condition"))')

					graph.append('_ifbody = _g.graph_add_node(_seq, _x+150, _y+100)')
					graph.append('_ifnode.node_find_pin("Then").make_link_to(_ifbody.node_find_pin("execute"))')
					for i,c in enumerate( b.body ):
						if i>=2:
							graph.append('_ifbody.node_create_pin(EEdGraphPinDirection.EGPD_Output, EdGraphPinType(PinCategory="exec"), "Then_%s")' %i)
						if is_print(c):
							graph.append('print("new sub print")')
							graph.append('_printnode = _g.graph_add_node_call_function(_print, _x+400, _y+150+%s)' %str(i*100))
							graph.append('_ifbody.node_find_pin("Then_%s").make_link_to(_printnode.node_find_pin("execute"))' %i)
							for item in c.values:
								if isinstance(item, ast.Name):
									vname = item.id
									graph.append('get_%s = _g.graph_add_node_variable_get("%s", None, _x+200, _y+150+%s)' %(vname,vname, i*100))
									graph.append('_printnode.node_find_pin("InString").make_link_to(get_%s.node_find_pin("%s"))' %(item.id, item.id))
					if b.orelse:
						graph.append('_elsebody = _g.graph_add_node(_seq, _x+150, _y+500)')
						graph.append('_ifnode.node_find_pin("Else").make_link_to(_elsebody.node_find_pin("execute"))')

						for i,c in enumerate( b.orelse ):
							if i>=2:
								graph.append('_elsebody.node_create_pin(EEdGraphPinDirection.EGPD_Output, pin_type, "Then_%s")' %i)
							if is_print(c):
								graph.append('print("new sub print")')
								graph.append('_printnode = _g.graph_add_node_call_function(_print, _x+400, _y+550+%s)' %str(i*100))
								graph.append('_elsebody.node_find_pin("Then_%s").make_link_to(_printnode.node_find_pin("execute"))' %i)
								for item in c.values:
									if isinstance(item, ast.Name):
										vname = item.id
										graph.append('get_%s = _g.graph_add_node_variable_get("%s", None, _x+200, _y+550+%s)' %(vname,vname, i*100))
										graph.append('_printnode.node_find_pin("InString").make_link_to(get_%s.node_find_pin("%s"))' %(item.id, item.id))


				elif is_print(b):
					graph.append('print("	new print")')
					graph.append('_x, _y = _g.graph_get_good_place_for_new_node()')
					graph.append('_printnode = _g.graph_add_node_call_function(_print, _x, _y)')
					graph.append('_mainnode.node_find_pin("Then_%s").make_link_to(_printnode.node_find_pin("execute"))' %then)
					for arg in b.args:
						print(arg)
						if isinstance(arg, ast.Name):
							vname = arg.id
							graph.append('get_%s = _g.graph_add_node_variable_get("%s", None, _x-100, _y)' %(vname,vname))
							graph.append('_printnode.node_find_pin("InString").make_link_to(get_%s.node_find_pin("%s"))' %(vname, vname))
						else:
							raise SyntaxError('can only print variables, not type: %s' %str(arg))

				then += 1

			self.blueprint_graph = graph
			script = '\n'.join(graph)
			if '--debug-unreal' in sys.argv:
				raise RuntimeError(script)

			#sdir = os.path.join( os.path.expanduser(UnrealGlue['project']), 'Content/Scripts')
			#if os.path.isdir(sdir):
			#	open(os.path.join(sdir, 'make_graph.py'), 'wb').write(script)

			self.graphs.append(script)
			return script

		else:
			#raise SyntaxError('invalid use of "with" statement: %s' %self.visit(node.context_expr))
			raise SyntaxError('invalid use of "with" statement: %s - got: %s' %(node.context_expr, self.visit(node.context_expr)))


unrealgen_test = '''
with unreal.MYblueprint:
	#from unreal.classes import MyCustomObject
	a = 'hello'
	b = 'world'
	c = 'foo bar'
	d = 'never printed'
	u = TArray( [1,2,3], type=int)
	w = TArray( [], type=int)
	for x in u:
		print(a)
		print(x)
		w.Add(x*2)

	#MyCustomObject::myloop( myarr=u, newarr=w )
	myloop( myarr=u, newarr=w )

	if foo(1):
		print(b)
		print(c)
	else:
		print(d)

'''

TODO_PYCPP = '''
class UMyCustomObject( UObject ):
	TArray<FMyCustomStruct> MyStructs;
	@UFUNCTION(BlueprintCallable, Category="MyCustomObject")
	def SetCustomStructs(const TArray<FMyCustomStruct>& Structs) ->bool:
		self.MyStructs = Structs
		return true
	@UFUNCTION( BlueprintPure, meta = {DisplayName:"Hello World", CompactNodeTitle:"HelloWorld", Keywords:"String Hello World"}, Category = Game )
	def HelloWorld() -> FText@:
		return FText::FromString(cstr("Hello World!"))
	@UFUNCTION()
	def foo( v:int ) -> bool:
		if v > 10:
			return true
		else:
			return false
	@UFUNCTION()
	def myloop( input TArray<int> myarr, output TArray<int> newarr ):
		for x in myarr:
			print(x)
			if foo( x ):
				break
			else:
				newarr.Add( x*2 )


'''

TODO = '''
	#def Get():
	#	return FModuleManager::LoadModuleChecked->[IMyPlugin](cstr("MyPlugin"))

	#def IsAvailable():
	#	return FModuleManager::Get()..IsModuleLoaded( cstr("MyPlugin") )

	#with unreal.blueprint(FMyCustomStruct):
	#	UPROPERTY(EditAnywhere, Category=Triangle)
	#	FVector Vertex0;
	#	UPROPERTY(EditAnywhere, Category=Triangle)
	#	FVector Vertex1;
	#	UPROPERTY(EditAnywhere, Category=Triangle)
	#	FVector Vertex2;


	def StartupModule():
		print 'TESTING MYBLUEPRINT...'

	def ShutdownModule():
		print 'MYBLUEPRINT EXIT'

'''

if __name__ == "__main__":
	a = UnrealGen('myblueprint', unrealgen_test)
	print(dir(ast))
	a.visit(ast.parse(unrealgen_test))
	print(a)
	print(a.get_gen_script())
