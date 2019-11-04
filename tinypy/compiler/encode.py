# -*- coding: utf-8 -*-
import tinypy.compiler.tokenize as tokenize
from tinypy.compiler.tokenize import Token
from tinypy.compiler.boot import *
from tinypy.compiler.interpreter_codes_gen import *
# moved to rebuild.py, which generates interpreter_codes_gen.py
#EOF,REGS,NAME,INTEGER,NUMBER,STRING,MOVE,IF,EQ,LE,LT, GGET,GSET, ADD,SUB,MUL,DIV,CMP,MGET,GET,SET,     NE,NOT,IFN,ITER,HAS,IGET,DEL,IFACE,DICT,LIST,PARAMS,LEN,JUMP,SETJMP,CALL,  DEF,RETURN,RAISE,NONE,MOD,LSH,RSH, POW,BITAND,BITOR,BITNOT,BITXOR,  PASS,FILE,DEBUG,POS = range(52)  ## note: POS is TP_ILINE in tp_vm.cpp

class DState:
	def __init__(self,code,fname):
		self.const_numbers = []  ## max size is 256
		self.header = []
		self.nopos = False
		self.code = code
		self.fname = fname
		self.lines = self.code.split('\n')
		self.stack,self.out,self._scopei,self.tstack,self._tagi,self.data = [],[('tag','EOF')],0,[],0,{}
		self.error = False

	def begin(self,gbl=False):
		if len(self.stack): self.stack.append((self.vars,self.r2n,self.n2r,self._tmpi,self.mreg,self.snum,self._globals,self.lineno,self.globals,self.rglobals,self.cregs,self.tmpc))
		else: self.stack.append(None)
		self.vars,self.r2n,self.n2r,self._tmpi,self.mreg,self.snum,self._globals,self.lineno,self.globals,self.rglobals,self.cregs,self.tmpc = [],{},{},0,0,str(self._scopei),gbl,-1,[],[],['regs'],0
		self._scopei += 1
		insert(self.cregs)

	def end(self):
		self.cregs.append(self.mreg)
		code(EOF)
		
		# This next line forces the encoder to
		# throw an exception if any tmp regs 
		# were leaked within the frame
		# assert(self.tmpc == 0) #REG
		if self.tmpc != 0:
			print("Warning:\nencode.py contains a register leak\n")
		
		if len(self.stack) > 1:
			self.vars,self.r2n,self.n2r,self._tmpi,self.mreg,self.snum,self._globals,self.lineno,self.globals,self.rglobals,self.cregs,self.tmpc = self.stack.pop()
		else: self.stack.pop()

	def const_number(self, n):
		## returns the address of the constant number
		if len(self.const_numbers) == 256:
			return -1
		elif n in self.const_numbers:
			return self.const_numbers.index(n)
		else:
			self.const_numbers.append(n)
			const_addr = len(self.const_numbers)-1
			code(NUMBER,a=0,b=2,c=const_addr, head=True)  ## b=2 means do not set a register
			write(fpack(number(n)), head=True)

			return const_addr


def insert(v): D.out.append(v)
def write(v, head=False):
	if istype(v,'list'):
		if head:
			D.header.append( v )
		else:
			insert(v)
		return
	for n in range(0,len(v),4):
		if head:
			D.header.append(('data',v[n:n+4]))
		else:
			insert(('data',v[n:n+4]))

def setpos(v, debug_mode='--debug' in sys.argv):
	if not debug_mode:
		return
	if D.nopos: return
	line,x = v
	if line == D.lineno: return
	text = D.lines[line-1]
	D.lineno = line
	val = text + "\0"*(4-len(text)%4)
	code_16(LINE,int(len(val)/4),line)
	write(val)

def code(i,a=0,b=0,c=0, head=False):
	if not istype(i,'number'): raise
	if not istype(a,'number'): raise
	if not istype(b,'number'): raise
	if not istype(c,'number'): raise
	write(('code',i,a,b,c), head=head)

def code_16(i,a,b):
	if b < 0: b += 0x8000
	code(i,a,(b&0xff00)>>8,(b&0xff)>>0)

def get_code16(i,a,b):
	return ('code',i,a,(b&0xff00)>>8,(b&0xff)>>0)

def _do_string(v,r=None):
	r = get_tmp(r)
	val = v + "\0"*(4-len(v)%4)
	code_16(STRING,r,len(v))
	write(val)
	return r
def do_string(t,r=None):
	return _do_string(t.val,r)

def _do_number(v,r=None):
	r = get_tmp(r)
	const_addr = D.const_number(v)
	if const_addr != -1:
		## TODO do not write number twice, this is needed until the rest of the code is refactored
		code(NUMBER,a=r,b=1,c=const_addr)
	else:
		code(NUMBER,a=r,b=0,c=0)
	write(fpack(number(v)))
	return r

def _do_integer(v,r=None):
	r = get_tmp(r)
	#code(INTEGER,r,0,0)
	#write(fpack(number(v)))  ## not packed or unpacked properly? TODO FIXME
	code(INTEGER, a=r, b=int(v), c=0)  ## just small integers for now
	return r

def do_number(t,r=None):
	if '--int-type' in sys.argv and '.' not in t.val and int(t.val) >= 0 and int(t.val) <= 255:
		return _do_integer(t.val,r)
	else:
		return _do_number(t.val,r)

def get_tag():
	k = str(D._tagi)
	D._tagi += 1
	return k
def stack_tag():
	k = get_tag()
	D.tstack.append(k)
	return k
def pop_tag():
	D.tstack.pop()

def tag(*t):
	t = D.snum+':'+':'.join([str(v) for v in t])
	insert(('tag',t))
def jump(*t):
	t = D.snum+':'+':'.join([str(v) for v in t])
	insert(('jump',t))
def setjmp(*t):
	t = D.snum+':'+':'.join([str(v) for v in t])
	insert(('setjmp',t))
def fnc(*t):
	t = D.snum+':'+':'.join([str(v) for v in t])
	r = get_reg(t)
	insert(('fnc',r,t))
	return r

def map_tags():
	tags = {}
	out = []
	n = 0
	for item in D.header + D.out:
		if item[0] == 'tag':
			tags[item[1]] = n
			continue
		if item[0] == 'regs':
			out.append(get_code16(REGS,item[1],0))
			n += 1
			continue
		out.append(item)
		n += 1
	for n in range(0,len(out)):
		item = out[n]
		if item[0] == 'jump':
			out[n] = get_code16(JUMP,0,tags[item[1]]-n)
		elif item[0] == 'setjmp':
			out[n] = get_code16(SETJMP,0,tags[item[1]]-n)
		elif item[0] == 'fnc':
			out[n] = get_code16(DEF,item[1],tags[item[2]]-n)
	for n in range(0,len(out)):
		item = out[n]
		if item[0] == 'data':
			out[n] = item[1]
		elif item[0] == 'code':
			i,a,b,c = item[1:]
			out[n] = chr(i)+chr(a)+chr(b)+chr(c)
		else:
			raise str(('huh?',item))
		if len(out[n]) != 4:
			raise ('code '+str(n)+' is wrong length '+str(len(out[n])))
	D.out = out

def get_tmp(r=None):
	if r != None: return r
	return get_tmps(1)[0]
def get_tmps(t):
	rs = alloc(t)
	regs = range(rs,rs+t)
	for r in regs:
		set_reg(r,"$"+str(D._tmpi))
		D._tmpi += 1
	D.tmpc += t #REG
	return regs
def alloc(t):
	s = ''.join(["01"[r in D.r2n] for r in range(0,min(256,D.mreg+t))])
	return s.index('0'*t)
def is_tmp(r):
	if r is None: return False
	return (D.r2n[r][0] == '$')
def un_tmp(r):
	n = D.r2n[r]
	free_reg(r)
	set_reg(r,'*'+n)
def free_tmp(r):
	if is_tmp(r): free_reg(r)
	return r
def free_tmps(r):
	for k in r: free_tmp(k)
def get_reg(n):
	if n not in D.n2r:
		set_reg(alloc(1),n)
	return D.n2r[n]
#def get_clean_reg(n):
	#if n in D.n2r: raise
	#set_reg(D.mreg,n)
	#return D.n2r[n]
def set_reg(r,n):
	D.n2r[n] = r; D.r2n[r] = n
	D.mreg = max(D.mreg,r+1)
def free_reg(r):
	if is_tmp(r): D.tmpc -= 1
	n = D.r2n[r]; del D.r2n[r]; del D.n2r[n]

def imanage(orig,fnc):
	if orig.val in ('+=', '-=', '*=', '/=') and '--beta' in sys.argv:
		print(orig)
		dest = orig.items[0]
		expr = orig.items[1]  ## may contain sub expressions
		assert len(orig.items)==2
		assert isinstance( dest, Token )
		if dest.type == 'name' and len(dest.val)==1:
			if expr.type == 'number' and expr.val.isdigit():
				b = int(expr.val)
				if b > 0 and b < 256:
					if orig.val == '+=':
						if dest.val in D.globals:
							code(92, a=ord(dest.val), b=b)
						else:
							if b == 1:
								code(90, a=get_reg(dest.val))
							else:
								code(91, a=get_reg(dest.val), b=b)
						return None
			if dest.val in D.globals:
				a = ord(dest.val)
				if expr.type == 'name' and len(expr.val)==1 and expr.val in D.globals:
					b = ord(expr.val)
					if orig.val == '+=':
						code(101, a=a, b=b)
					elif orig.val == '-=':
						code(102, a=a, b=b)
					elif orig.val == '*=':
						code(103, a=a, b=b)
					elif orig.val == '/=':
						code(104, a=a, b=b)
					return None
				elif expr.type == 'symbol':
					opb, opc = expr.items
					if opb.type=='name' and len(opb.val)==1 and opb.val in D.globals:
						if opc.type=='name' and len(opc.val)==1 and opc.val in D.globals:
							b = ord(opb.val)
							c = ord(opc.val)
							if orig.val == '+=':
								if expr.val == '+':
									code(105, a=a, b=b, c=c)
								elif expr.val == '-':
									code(106, a=a, b=b, c=c)
								elif expr.val == '*':
									code(107, a=a, b=b, c=c)
								elif expr.val == '/':
									code(108, a=a, b=b, c=c)

								return None

	items = orig.items
	orig.val = orig.val[:-1]
	t = Token(orig.pos,'symbol','=',[items[0],orig])
	return fnc(t)

def unary(i,tb,r=None):
	r = get_tmp(r)
	b = do(tb)
	code(i,r,b)
	if r != b: free_tmp(b)
	return r
def infix(i,tb,tc,r=None):
	r = get_tmp(r)
	b,c = do(tb,r),do(tc)
	code(i,r,b,c)
	if r != b: free_tmp(b)
	free_tmp(c)
	return r
def logic_infix(op, tb, tc, _r=None):
	t = get_tag() 
	r = do(tb, _r)
	if _r != r: free_tmp(_r) #REG
	if op == 'and':   code(IF, r)
	elif op == 'or':  code(IFN, r)
	jump(t, 'end')
	_r = r
	r = do(tc, _r)
	if _r != r: free_tmp(_r) #REG
	tag(t, 'end')
	return r

def _do_none(r=None):
	r = get_tmp(r)
	code(NONE,r)
	return r

def do_symbol(t,r=None):
	sets = ['=']
	isets = ['+=','-=','*=','/=', '|=', '&=', '^=']
	cmps = ['<','>','<=','>=','==','!=']
	metas = {
		'+':ADD,'*':MUL,'/':DIV,'**':POW,
		'-':SUB,
		'%':MOD,'>>':RSH,'<<':LSH,
		'&':BITAND,'|':BITOR,'^':BITXOR,
	}
	if t.val == 'None': return _do_none(r)
	if t.val == 'True':
		return _do_number('1',r)
	if t.val == 'False':
		return _do_number('0',r)
	items = t.items

	if t.val in ['and','or']:
		return logic_infix(t.val, items[0], items[1], r)
	if t.val in isets:
		return imanage(t,do_symbol)
	if t.val == 'is':
		return infix(EQ,items[0],items[1],r)
	if t.val == 'isnot':
		return infix(CMP,items[0],items[1],r)
	if t.val == 'not':
		return unary(NOT, items[0], r)
	if t.val == 'in':
		return infix(HAS,items[1],items[0],r)
	if t.val == 'notin':
		r = infix(HAS,items[1],items[0],r)
		zero = _do_number('0')
		code(EQ,r,r,free_tmp(zero))
		return r
	if t.val in sets:
		if items[0].type == 'name' and items[0].val in D.globals and len(items[0].val)==1:
			a = items[0]
			expr = items[1]
			if expr.type == 'symbol' and expr.val in '+-/*':
				b = expr.items[0]
				c = expr.items[1]
				if b.type == 'name' and c.type == 'name' and len(b.val)==1 and len(c.val)==1:
					if b.val in D.globals and c.val in D.globals:
						if expr.val == '+':
							code(68, a=ord(a.val), b=ord(b.val), c=ord(c.val))
						elif expr.val == '-':
							code(69, a=ord(a.val), b=ord(b.val), c=ord(c.val))
						elif expr.val == '*':
							code(70, a=ord(a.val), b=ord(b.val), c=ord(c.val))
						elif expr.val == '/':
							code(71, a=ord(a.val), b=ord(b.val), c=ord(c.val))
						return None

		return do_set_ctx(items[0],items[1]);

	elif t.val in cmps:
		b,c = items[0],items[1]
		v = t.val
		if v[0] in ('>','>='):
			b,c,v = c,b,'<'+v[1:]
		cd = EQ
		if v == '<': cd = LT
		if v == '<=': cd = LE
		if v == '!=': cd = NE
		return infix(cd,b,c,r)
	else:
		#	if t.val in D.vars:
		#return do_local(t,r)
		a = items[0]
		b = items[1]
		if a.type == 'name' and a.val in D.globals and len(a.val)==1:
			if b.type == 'name' and b.val in D.globals and len(b.val)==1:
				print('r=', r)
				if r is None:
					r = 0
				if t.val == '+':
					code(64, a=r, b=ord(a.val), c=ord(b.val))
					return r
				elif t.val == '-':
					code(65, a=r, b=ord(a.val), c=ord(b.val))
					return r
				elif t.val == '*':
					code(66, a=r, b=ord(a.val), c=ord(b.val))
					return r
				elif t.val == '/':
					code(67, a=r, b=ord(a.val), c=ord(b.val))
					return r

		return infix(metas[t.val],items[0],items[1],r)

def do_set_ctx(k,v):
	if k.type == 'name':
		if (D._globals and k.val not in D.vars) or (k.val in D.globals):
			c = do_string(k)
			b = do(v)
			code(GSET,c,b)
			free_tmp(c)
			free_tmp(b)
			return
		a = do_local(k)
		b = do(v)
		code(MOVE,a,b)
		free_tmp(b)
		return a
	elif k.type in ('tuple','list'):
		if v.type in ('tuple','list'):
			n,tmps = 0,[]
			for kk in k.items:
				vv = v.items[n]
				tmp = get_tmp(); tmps.append(tmp)
				r = do(vv)
				code(MOVE,tmp,r)
				free_tmp(r) #REG
				n+=1
			n = 0
			for kk in k.items:
				vv = v.items[n]
				tmp = tmps[n]
				free_tmp(do_set_ctx(kk,Token(vv.pos,'reg',tmp))) #REG
				n += 1
			return

		r = do(v); un_tmp(r)
		n, tmp = 0, Token(v.pos,'reg',r)
		for tt in k.items:
			free_tmp(do_set_ctx(tt,Token(tmp.pos,'get',None,[tmp,Token(tmp.pos,'number',str(n))]))) #REG
			n += 1
		free_reg(r)
		return

	r = do(k.items[0])
	rr = do(v)
	tmp = do(k.items[1])
	code(SET,r,tmp,rr)
	free_tmp(r) #REG
	free_tmp(tmp) #REG
	return rr

def manage_seq(i,a,items,sav=0):
	l = max(sav,len(items))
	n,tmps = 0,get_tmps(l)
	for tt in items:
		r = tmps[n]
		b = do(tt,r)
		if r != b:
			code(MOVE,r,b)
			free_tmp(b)
		n +=1
	if not len(tmps):
		code(i,a,0,0)
		return 0
	code(i,a,tmps[0],len(items))
	free_tmps(tmps[sav:])
	return tmps[0]

def p_filter(items):
	a,b,c,d = [],[],None,None
	for t in items:
		if t.type == 'symbol' and t.val == '=': b.append(t)
		elif t.type == 'args': c = t
		elif t.type == 'nargs': d = t
		else: a.append(t)
	return a,b,c,d

def do_import(t):
	if len(t.items) == 1:
		mod = t.items[0]
		name = mod
	else:
		mod, name = t.items

	mod.type = 'string'
	v = do_call(Token(t.pos,'call',None,[
		Token(t.pos,'name','__import__'),
		mod,
		Token(t.pos, 'symbol', 'None')]
		))

	name.type = 'name'
	do_set_ctx(name,Token(t.pos,'reg',v))

def do_from(t):
	mod = t.items[0]
	items = t.items[1]
	mod.type = 'string'

	if items.type == 'args':
		# it really shouldn't be args -- need to fix the parser.
		if items.val == '*':
			items.type = 'string'
	elif items.type == 'name':
		items.type = 'string'
		items = Token(items.pos, 'tuple', None, [items])
	elif items.type ==  'tuple':
		for item in items.items:
			item.type = 'string'
	else: 
		tokenize.u_error('SyntaxError', D.code, t.pos)

	v = do(Token(t.pos,'call',None,[
		Token(t.pos,'name','__import__'),
		mod,
		items,
		]))

	un_tmp(v)

	free_tmp(do(Token(t.pos, 'call', None, [
			Token(t.pos, 'name', '__merge__'),
			Token(t.pos, 'name', '__dict__'),
			Token(t.pos, 'reg', v) #REG
			]
		)))

	free_reg(v)
 
def do_globals(t):
	for t in t.items:
		if t.val not in D.globals:
			D.globals.append(t.val)

def do_del(tt):
	for t in tt.items:
		if t.type=='name':
			r = do(t)
			code(DEL, r)
			free_tmp(r)
		else:  ## assume dictionary `del foo['bar']`
			r = do(t.items[0])
			r2 = do(t.items[1])
			code(DEL,r,r2)
			free_tmp(r)
			free_tmp(r2)

def do_call(t,r=None):
	assert t.type == 'call'
	## fast printing optimization
	if t.items[0].type == 'name' and t.items[0].val == 'print':
		if len(t.items[1:]) >= 2 and t.items[-1].type == 'symbol' and t.items[-1].val == '=':
			kwargs = t.items[-1]
			if kwargs.items[0].type=='name' and kwargs.items[0].val == 'end':
				if kwargs.items[1].type=='string' and kwargs.items[1].val == '':
					if t.items[1].type == 'string':
						if len(t.items[1].val)==1:
							code(60, a=ord(t.items[1].val))
							return None
						## TODO fix unicode bugs, and test compiler with Python3
						elif len(t.items[1].val)==2 and t.items[1].val == '·':  ## middle dot with bad encoding
							#code(60, a=ord(u'·'))  ## code 183, is printed as `�`
							code(60, a=ord('.'))  ## workaround change to a regular dot
							return None

	r = get_tmp(r)
	items = t.items
	fnc = do(items[0])
	a,b,c,d = p_filter(t.items[1:])
	e = None
	if len(b) != 0 or d != None:
		e = do(Token(t.pos,'dict',None,[])); un_tmp(e);
		for p in b:
			p.items[0].type = 'string'
			t1,t2 = do(p.items[0]),do(p.items[1])
			code(SET,e,t1,t2)
			free_tmp(t1); free_tmp(t2) #REG
		if d: free_tmp(do(
			Token(t.pos,'call',None,
				[ Token(t.pos,'name', '__merge__'),
				  Token(t.pos,'reg',e),
				  d.items[0]
				]))) #REG
	manage_seq(PARAMS,r,a)
	if c != None:
		t1,t2 = _do_string('*'),do(c.items[0])
		code(SET,r,t1,t2)
		free_tmp(t1); free_tmp(t2) #REG
	if e != None:
		t1 = _do_none()
		code(SET,r,t1,e)
		free_tmp(t1) #REG
	code(CALL,r,fnc,r)
	free_tmp(fnc) #REG
	return r

def do_name(t,r=None):
	if t.val in D.vars:
		return do_local(t,r)
	if t.val not in D.rglobals:
		D.rglobals.append(t.val)
	r = get_tmp(r)
	c = do_string(t)
	code(GGET,r,c)
	free_tmp(c)
	return r

def do_local(t,r=None):
	if t.val in D.rglobals:
		D.error = True
		tokenize.u_error('UnboundLocalError',D.code,t.pos)
	if t.val not in D.vars:
		D.vars.append(t.val)
	return get_reg(t.val)

def do_def(tok,kls=None):
	items = tok.items

	t = get_tag()
	rf = fnc(t,'end')

	D.begin()
	setpos(tok.pos)
	r = do_local(Token(tok.pos,'name','__params'))
	do_info(items[0].val)
	a,b,c,d = p_filter(items[1].items)
	for p in a:
		v = do_local(p)
		tmp = _do_none()
		code(GET,v,r,tmp)
		free_tmp(tmp) #REG
	for p in b:
		v = do_local(p.items[0])
		do(p.items[1],v)
		tmp = _do_none()
		code(IGET,v,r,tmp)
		free_tmp(tmp) #REG
	if c != None:
		v = do_local(c.items[0])
		tmp = _do_string('*')
		code(GET,v,r,tmp)
		free_tmp(tmp) #REG
	if d != None:
		e = do_local(d.items[0])
		code(DICT,e,0,0)
		tmp = _do_none()
		code(IGET,e,r,tmp)
		free_tmp(tmp) #REG
	free_tmp(do(items[2])) #REG
	D.end()

	tag(t,'end')

	if kls == None:
		if D._globals: do_globals(Token(tok.pos,0,0,[items[0]]))
		r = do_set_ctx(items[0],Token(tok.pos,'reg',rf))
	else:
		rn = do_string(items[0])
		code(SET,kls,rn,rf)
		free_tmp(rn)

	free_tmp(rf)

def do_class(t):
	tok = t
	items = t.items
	parent = None
	if items[0].type == 'name':
		name = items[0].val
		parent = Token(tok.pos,'name','object')
	else:
		name = items[0].items[0].val
		parent = items[0].items[1]

	kls = do_classdecl()
	un_tmp(kls)
	ts = _do_string(name)
	code(GSET,ts,kls)
	free_tmp(ts) #REG
	
	free_tmp(do(Token(tok.pos,'call',None,[
		Token(tok.pos,'name','setmeta'),
		Token(tok.pos,'reg',kls),
		parent])))
		
	for member in items[1].items:
		if member.type == 'def': do_def(member,kls)
		elif member.type == 'symbol' and member.val == '=': do_classvar(member,kls)
		else: continue
		
	free_reg(kls) #REG

def do_classdecl():
	r = get_tmp(None)
	manage_seq(IFACE, r, [])
	return r

def do_classvar(t,r):
	var = do_string(t.items[0])
	val = do(t.items[1])
	code(SET,r,var,val)
	free_reg(var)
	free_reg(val)

## hartsantler
#def do_loop_old_hack(t):
#    LOOP = int(t.val) + 100
#    code(LOOP)
#    items = t.items
#    t = stack_tag()
#    body = do(items[0])
#    pop_tag()

def do_loop(t):
	#s = stack_tag()

	items = t.items
	#LOOP_NUM = 99
	#code(LOOP_NUM, int(t.val))  ## this works, just read from VA
	#LOOP = 100
	#code(LOOP)
	LOOP = 100
	#code(LOOP, int(t.val))  ## this still wont work with large loops, the second arg is register A, and that can only be 8bits
	#code_16(LOOP, a=0, b=int(t.val))  ## not sure how this works
	r = do_number(t.num_loops)
	code(LOOP, r)
	free_tmp(r)
	#t = stack_tag()
	#tag(t,'begin')

	#raise RuntimeError(items)
	#t = stack_tag()
	body = do(items[0])
	#free_tmp(body)
	#tag(t,'end')
	#pop_tag()


def do_while(t):
	items = t.items
	t = stack_tag()
	tag(t,'begin')
	tag(t,'continue')
	cond = items[0]
	old_style = True
	if cond.type == 'symbol':
		if cond.val == '<':
			if cond.items[0].type == 'name' and cond.items[1].type == 'number' and cond.items[0].val not in D.globals:
				const_addr = D.const_number(cond.items[1].val)
				if const_addr != -1:
					if items[1].type == 'statements':
						old_style = False
						a, b = cond.items
						## look ahead to see if the next operation is to increment a.val by 1
						do_increment = 0
						do_slower_method = True

						nextop = items[1].items[0]
						if nextop.type == 'symbol' and nextop.val == '+=':
							if nextop.items[0].type == 'name' and nextop.items[1].type == 'number' and nextop.items[1].val.isdigit():
								incby = int(nextop.items[1].val)
								if nextop.items[0].val == a.val and incby >= 1 and incby <= 255:
									items[1].items = items[1].items[1:]  ## remove the next op
									if incby == 1:
										## this is optimized more because of `i++`
										code(80, a=get_reg(a.val), b=const_addr)
										do_slower_method = False
									else:
										do_increment = incby

						if do_slower_method:
							code(81, a=get_reg(a.val), b=const_addr, c=do_increment)

			elif cond.items[0].type == 'name' and cond.items[1].type == 'name':
				a,b = cond.items
				if len(b.val)==1 and b.val in D.globals:
					if len(a.val)==1 and a.val in D.globals:
						old_style = False
						code(82, a=ord(a.val), b=ord(b.val))
					elif a.val not in D.globals:
						old_style = False
						code(83, a=get_reg(a.val), b=ord(b.val))

	if old_style:
		r = do(items[0])
		code(IF,r)
		free_tmp(r) #REG

	jump(t,'end')
	free_tmp(do(items[1])) #REG
	jump(t,'begin')
	tag(t,'break')
	tag(t,'end')
	pop_tag()

def do_for(tok):
	items = tok.items

	reg = get_tmp()
	itr = do(items[1])
	i = _do_number('0')

	t = stack_tag(); tag(t,'loop'); tag(t,'continue')
	code(ITER,reg,itr,i); jump(t,'end')
	free_tmp(do_set_ctx(items[0], Token(tok.pos, 'reg', reg)))
	free_tmp(do(items[2])) #REG
	jump(t,'loop')
	tag(t,'break'); tag(t,'end'); pop_tag()

	free_tmp(itr) #REG
	free_tmp(i)

def do_comp(t,r=None):
	name = 'comp:'+get_tag()
	r = do_local(Token(t.pos,'name',name))
	code(LIST,r,0,0)
	key = Token(t.pos,'get',None,[
			Token(t.pos,'reg',r),
			Token(t.pos,'symbol','None')])
	ap = Token(t.pos,'symbol','=',[key,t.items[0]])
	do(Token(t.pos,'for',None,[t.items[1],t.items[2],ap]))
	return r

def do_if(t):
	items = t.items
	t = get_tag()
	n = 0
	for tt in items:
		tag(t,n)
		if tt.type == 'elif':
			slow_if = True
			if tt.items[0].type == 'symbol' and tt.items[0].val == '<=':
				opa, opb = tt.items[0].items
				if opa.type == 'symbol' and  opa.val == '+':
					opaa, opab = opa.items
					if opaa.type=='name' and opab.type=='name':
						if len(opaa.val)==1 and opaa.val in D.globals:
							if len(opab.val)==1 and opab.val in D.globals:
								if opb.type == 'number' and opb.val.isdigit():
									num = int(opb.val)
									if num >= 0 and num <= 255:
										slow_if = False
										code(128, a=ord(opaa.val), b=ord(opab.val), c=num)

			if slow_if:
				a = do(tt.items[0])
				code(IF,a)
				free_tmp(a);

			jump(t,n+1)
			free_tmp(do(tt.items[1])) #REG
		elif tt.type == 'else':
			free_tmp(do(tt.items[0])) #REG
		else:
			raise
		jump(t,'end')
		n += 1
	tag(t,n)
	tag(t,'end')

def do_try(t):
	items = t.items
	t = get_tag()
	setjmp(t,'except')
	free_tmp(do(items[0])) #REG
	code(SETJMP,0)
	jump(t,'end')
	tag(t,'except')
	free_tmp(do(items[1].items[1])) #REG
	tag(t,'end')

def do_return(t):
	if t.items: r = do(t.items[0])
	else: r = _do_none()
	code(RETURN,r)
	free_tmp(r)
	return

def do_assert(t):
	if t.items: r = do(t.items[0])
	else: r = _do_none()

	un_tmp(r)
	v = do_call(Token(t.pos,'call',None,[
		Token(t.pos,'name','__assert__'),
		Token(t.pos, 'reg', r) #REG
		]
		))

	free_tmp(v)
	return

def do_raise(t):
	if t.items: r = do(t.items[0])
	else: r = _do_none()
	code(RAISE,r)
	free_tmp(r)
	return

def do_statements(t):
	for tt in t.items: free_tmp(do(tt))

def do_list(t,r=None):
	r = get_tmp(r)
	manage_seq(LIST,r,t.items)
	return r

def do_dict(t,r=None):
	r = get_tmp(r)
	manage_seq(DICT,r,t.items)
	return r

def do_get(t,r=None):
	items = t.items
	return infix(GET,items[0],items[1],r)

def do_mget(t,r=None):
	items = t.items
	return infix(MGET,items[0],items[1],r)

def do_break(t): jump(D.tstack[-1],'break')
def do_continue(t): jump(D.tstack[-1],'continue')
def do_pass(t): code(PASS)

def do_info(name='?'):
	if D.nopos: return
	code(FILE,free_tmp(_do_string(D.fname)))
	code(NAME,free_tmp(_do_string(name)))
def do_module(t):
	do_info()
	free_tmp(do(t.items[0])) #REG
def do_reg(t,r=None): return t.val

fmap = {
	'loop': do_loop,  ## hartsantler, sept21
	'module':do_module,'statements':do_statements,'def':do_def,
	'return':do_return, 'assert':do_assert, 'while':do_while,'if':do_if,
	'break':do_break,'pass':do_pass,'continue':do_continue,'for':do_for,
	'class':do_class,'raise':do_raise,'try':do_try,'import':do_import,
	'globals':do_globals,'del':do_del,'from':do_from,
}
rmap = {
	'list':do_list, 'tuple':do_list, 'dict':do_dict, 'slice':do_list,
	'comp':do_comp, 'name':do_name,'symbol':do_symbol,'number':do_number,
	'string':do_string,'get':do_get, 'mget':do_mget, 'call':do_call, 'reg':do_reg,
}

def do(t,r=None):
	if t.pos: setpos(t.pos)
	#try:
	if 1:
		if t.type in rmap:
			return rmap[t.type](t,r)
		#if r != None: free_reg(r) #REG
		return fmap[t.type](t)
	#except:
	#    raise
	#    if D.error: raise
	#    D.error = True
	#    tokenize.u_error('encode',D.code,t.pos)

def encode(fname,s,t):
	t = Token((1,1),'module','module',[t])
	global D
	s = tokenize.clean(s)
	D = DState(s,fname)
	D.begin(True)
	do(t)
	D.end()
	if '--inspect-bytecode' in sys.argv or '--beta' in sys.argv:
		print(D.out)
		for chunk in D.out:
			print(chunk)

	map_tags()
	out = []
	for part in D.out:
		if type(part) is str:
			out.append(part.encode('latin1'))
		else:
			out.append(part)
	D = None
	# Use a function instead of ''.join() so that bytes and
	# strings during bootstrap
	if '--inspect-bytecode' in sys.argv:
		print(out)

	return b''.join(out)

