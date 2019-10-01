#include <iostream>

/* write to standard output */
void tp_default_echo(const char* string, int length) {
	if(length < 0) length = strlen(string);
	fwrite(string, 1, length, stdout);
}

/* File: VM
 * Functionality pertaining to the virtual machine.
 */

tp_vm * tp_create_vm(void) {
	int i;
	tp_vm *tp = (tp_vm*)calloc(sizeof(tp_vm),1);
	tp->time_limit = TP_NO_LIMIT;
	tp->clocks = clock();
	tp->time_elapsed = 0.0;
	tp->mem_limit = TP_NO_LIMIT;
	tp->mem_exceeded = 0;
	tp->mem_used = sizeof(tp_vm);
	tp->cur = 0;
	tp->jmp = 0;
	tp->ex = tp_None;

	tp->root = tp_list_nt(tp); /* root is not tracked by gc, as gc is not defined yet.*/
	tp->echo = tp_default_echo;

	for (i=0; i<256; i++) { tp->chars[i][0]=i; }

	tp_gc_init(tp);

	tp->_list_meta = tp_interface_t(tp);
	tp->_dict_meta = tp_interface_t(tp);
	tp->_string_meta = tp_interface_t(tp);

	
	/* gc initialized, can use tpy_ functions. */
	tp->_regs = tp_list_t(tp);
	for (i=0; i<TP_REGS; i++) { tp_set(tp, tp->_regs, tp_None, tp_None); }
	tp->modules = tp_dict_t(tp);
	tp->_params = tp_list_t(tp);

	for (i=0; i<TP_FRAMES; i++) { tp_set(tp, tp->_params, tp_None, tp_list_t(tp)); }

	tp_set(tp, tp->root, tp_None, tp->builtins);
	tp_set(tp, tp->root, tp_None, tp->modules);
	tp_set(tp, tp->root, tp_None, tp->_regs);
	tp_set(tp, tp->root, tp_None, tp->_params);

	tp->builtins = tp_import(tp, tp_string_atom(tp, "__builtins__"), tp_None, tp_string_atom(tp, "<builtins>"));

	tp_set(tp, tp->root, tp_None, tp->_list_meta);
	tp_set(tp, tp->root, tp_None, tp->_dict_meta);
	tp_set(tp, tp->root, tp_None, tp->_string_meta);
	
	
	tp->regs = tp->_regs.list.val->items;
	tp->last_result = tp_None;
	tp_full(tp);
	return tp;
}

void tp_enter_frame(TP, tp_obj globals, tp_obj code, tp_obj * ret_dest) {
	tpd_frame f = tp_frame_nt(tp, globals, code, ret_dest);

	//if (f.regs+(256+TP_REGS_EXTRA) >= tp->regs+TP_REGS || tp->cur >= TP_FRAMES-1) {
	//    tp_raise(,tp_string_atom(tp, "(tp_frame) RuntimeError: stack overflow"));
	//}

	if (f.regs+(256+TP_REGS_EXTRA) >= tp->regs+TP_REGS) {
		throw "StackOverflowError in tp_vm.cpp:tp_enter_frame (f.regs+(256+TP_REGS_EXTRA) >= tp->regs+TP_REGS)";
	}
	if (tp->cur >= TP_FRAMES-1) {
		throw "StackOverflowError in tp_vm.cpp:tp_enter_frame (tp->cur >= TP_FRAMES-1)";
	}

	tp->cur += 1;
	tp->frames[tp->cur] = f;
}

void _tp_raise_DEPRECATED(TP, tp_obj e) {
	/*char *x = 0; x[0]=0;*/
	if (!tp || !tp->jmp) {
#ifndef CPYTHON_MOD
		tp->echo("\nException:\n", -1); tp_echo(tp,e); tp->echo("\n", -1);
		abort();
		exit(-1);
#else
		tp->ex = e;
		longjmp(tp->nextexpr,1);
#endif
	}
	if (e.type.type_id != TP_NONE) { tp->ex = e; }
	tp_grey(tp,e);
	abort();
	longjmp(tp->buf,1);
}

void _tp_raise(TP, tp_obj e) {
	std::cout << std::endl << "tp_vm.cpp _tp_raise (RAISE RUNTIME ERROR)" << std::endl;
	tp_obj message = tp_str(tp, e);
	std::cout << "  error message: " << message.string.val << std::endl;
	std::cout << "  object type: " << e.type.type_id << std::endl;
	throw message.string.val;
}

void tp_print_stack(TP) {
	int i;
	tp->echo("\n", -1);
	for (i=0; i<=tp->cur; i++) {
		if (!tp->frames[i].lineno) { continue; }
		tp->echo("File \"", -1); tp_echo(tp,tp->frames[i].fname); tp->echo("\", ", -1);
		tp_echo(tp, tp_printf(tp, "line %d, in ",tp->frames[i].lineno));
		tp_echo(tp,tp->frames[i].name); tp->echo("\n ", -1);
		tp_echo(tp,tp->frames[i].line); tp->echo("\n", -1);
	}
	tp->echo("\nException:\n", -1); tp_echo(tp,tp->ex); tp->echo("\n", -1);
}


void tp_handle(TP) {
	int i;
	for (i=tp->cur; i>=0; i--) {
		if (tp->frames[i].jmp) { break; }
	}
	if (i >= 0) {
		tp->cur = i;
		tp->frames[i].cur = tp->frames[i].jmp;
		tp->frames[i].jmp = 0;
		return;
	}
#ifndef CPYTHON_MOD
	tp_print_stack(tp);
	exit(-1);
#else
	longjmp(tp->nextexpr,1);
#endif
}


int tp_step(TP);
void tp_continue_frame(TP, int cur) {
	jmp_buf tmp;
	memcpy(tmp, tp->buf, sizeof(jmp_buf));
	tp->jmp += 1;
	if (setjmp(tp->buf)) {
		tp_handle(tp);
	}
	/* keep runing till the frame drops back (aka function returns) */
	while (tp->cur >= cur) {
		if (tp_step(tp) == -1) break;
	}

	tp->jmp -= 1;
	memcpy(tp->buf, tmp, sizeof(jmp_buf));
}

/* run the current frame till it returns */
void tp_run_frame(TP) {
	tp_continue_frame(tp, tp->cur);
}


void tp_return(TP, tp_obj v) {
	tp_obj *dest = tp->frames[tp->cur].ret_dest;
	if (dest) { *dest = v; tp_grey(tp,v); }
/*     memset(tp->frames[tp->cur].regs,0,TP_REGS_PER_FRAME*sizeof(tp_obj));
	   fprintf(stderr,"regs:%d\n",(tp->frames[tp->cur].cregs+1));*/
	memset(tp->frames[tp->cur].regs-TP_REGS_EXTRA,0,(TP_REGS_EXTRA+tp->frames[tp->cur].cregs)*sizeof(tp_obj));
	tp->cur -= 1;
}

/*
enum {
	TP_IEOF,TP_IADD,TP_ISUB,TP_IMUL,TP_IDIV,TP_IPOW,TP_IBITAND,TP_IBITOR,TP_ICMP,TP_IMGET,TP_IGET,TP_ISET,
	TP_INUMBER,TP_ISTRING,TP_IGGET,TP_IGSET,TP_IMOVE,TP_IDEF,TP_IPASS,TP_IJUMP,TP_ICALL,
	TP_IRETURN,TP_IIF,TP_IDEBUG,TP_IEQ,TP_ILE,TP_ILT,TP_IIFACE, TP_IDICT,TP_ILIST,TP_INONE,TP_ILEN,
	TP_ILINE,TP_IPARAMS,TP_IIGET,TP_IFILE,TP_INAME,TP_INE,TP_IHAS,TP_IRAISE,TP_ISETJMP,
	TP_IMOD,TP_ILSH,TP_IRSH,TP_IITER,TP_IDEL,TP_IREGS,TP_IBITXOR, TP_IIFN, 
	TP_INOT, TP_IBITNOT,
	TP_ITOTAL
};
const char *tp_strings[TP_ITOTAL] = {
	   "EOF","ADD","SUB","MUL","DIV","POW","BITAND","BITOR","CMP","MGET", "GET","SET","NUM",
	   "STR","GGET","GSET","MOVE","DEF","PASS","JUMP","CALL","RETURN","IF","DEBUG",
	   "EQ","LE","LT","IFACE","DICT","LIST","NONE","LEN","LINE","PARAMS","IGET","FILE",
	   "NAME","NE","HAS","RAISE","SETJMP","MOD","LSH","RSH","ITER","DEL","REGS",
	   "BITXOR", "IFN", "NOT", "BITNOT",
};
*/

enum {
	TP_IEOF,  // this must be first, otherwise segfault in case of TP_INUMBER
	TP_IREGS,
	TP_INAME,
	TP_IINTEGER,
	TP_INUMBER,TP_ISTRING,
	TP_IMOVE,
	TP_IIF,TP_IEQ,TP_ILE,TP_ILT,
	TP_IGGET,TP_IGSET,

	TP_IADD,TP_ISUB,TP_IMUL,TP_IDIV,TP_ICMP,
	TP_IMGET,TP_IGET,TP_ISET,

	TP_INE,
	TP_INOT, 
	TP_IIFN, 
	TP_IITER,
	TP_IHAS,
	TP_IIGET,
	TP_IDEL, 
	TP_IIFACE, TP_IDICT,TP_ILIST,
	TP_IPARAMS,
	TP_ILEN,
	TP_IJUMP,
	TP_ISETJMP,
	TP_ICALL,
	TP_IDEF,
	TP_IRETURN,
	TP_IRAISE,
	TP_INONE,
	TP_IMOD,TP_ILSH,TP_IRSH,
	TP_IPOW,TP_IBITAND,TP_IBITOR, TP_IBITNOT, TP_IBITXOR,

	TP_IPASS,
	TP_IFILE,
	TP_IDEBUG,
	TP_ILINE,
	TP_ITOTAL
};

const char *tp_strings[TP_ITOTAL] = {
	"EOF",
	"REGS",
	"NAME",
	"INTEGER",
	"NUM", "STR",
	"MOVE",
	"IF", "EQ","LE","LT",
	"GGET","GSET",

	"ADD","SUB","MUL","DIV","CMP","MGET", "GET","SET",

	"NE",
	"NOT", 
	"IFN", 
	"ITER",
	"HAS",
	"IGET",
	"DEL",
	"IFACE","DICT","LIST",
	"PARAMS",
	"LEN",
	"JUMP",
	"SETJMP",
	"CALL",
	"DEF",
	"RETURN",
	"RAISE",
	"NONE",
	"MOD","LSH","RSH",
	"POW","BITAND","BITOR","BITNOT", "BITXOR", 

	"PASS",
	"FILE",
	"DEBUG",
	"LINE",
};

#define VA ((int)e.regs.a)
#define VB ((int)e.regs.b)
#define VC ((int)e.regs.c)
#define RA regs[e.regs.a]
#define RB regs[e.regs.b]
#define RC regs[e.regs.c]
#define UVBC (unsigned short)(((VB<<8)+VC))
#define SVBC (short)(((VB<<8)+VC))
#define GA tp_grey(tp,RA)
#define SR(v) f->cur = cur; return(v);


char * TP_xSTR(TP, tp_obj obj) {
	return tp_cstr(tp, tp_str(tp, obj));
}

tp_obj __global_objects__[256] = {};

int tp_step(TP) {
	tpd_frame *f = &tp->frames[tp->cur];
	tp_obj *regs = f->regs;
	tpd_code *cur = f->cur;

	while(1) {
	#ifdef TP_SANDBOX
		printf("WARN SANDBOX MODE\n");
		tp_bounds(tp,cur,1);
	#endif

	tpd_code e = *cur;

	#ifdef DEBUG
		if (e.i < TP_ITOTAL)
			fprintf(stdout,"%2d.%4d: %-6s %3d %3d %3d\n",tp->cur,cur - (tpd_code*)f->code.string.info->s,tp_strings[e.i],VA,VB,VC);
	#endif

if ( e.i == 90 ) {
	#ifdef DEBUG
		std::cout << "TP_POST_INC ++" << std::endl;
		std::cout << "  RA: " << tp_as_string(tp, RA) << std::endl;
		std::cout << "  RB: " << tp_as_string(tp, RB) << std::endl;
		std::cout << "  RC: " << tp_as_string(tp, RC) << std::endl;
		std::cout << "VA: " << VA << std::endl;
		std::cout << "VB: " << VB << std::endl;
		std::cout << "VC: " << VC << std::endl;
	#endif

	if (RA.type.type_id == TP_INTEGER)
		RA.integer.val ++;
	else
		RA.number.val ++;

} else if ( e.i == 102 ) {
	#ifdef DEBUG
		std::cout << "VA: " << (char)VA << std::endl;
		std::cout << "VB: " << (char)VB << std::endl;
		std::cout << "VC: " << (char)VC << std::endl;
	#endif

	// 3x faster!
	tp_obj a = __global_objects__[VA];
	tp_obj b = __global_objects__[VB];
	tp_obj c = __global_objects__[VC];
	if (RA.type.type_id == TP_INTEGER)
		a.integer.val += b.integer.val + c.integer.val;
	else
		a.number.val += b.number.val + c.number.val;
	__global_objects__[VA] = a;


} else {

	switch (e.i) {
		case TP_IEOF: tp->last_result = RA; tp_return(tp,tp_None); SR(0); break;
		case TP_IREGS: f->cregs = VA; break;

		case TP_INAME: {
			f->name = RA;
			#ifdef DEBUG
				std::cout << "  RA: " << tp_as_string(tp, RA) << std::endl;
			#endif
		} break;

		case TP_IINTEGER: {
			RA = tp_integer( VB );
			//RA = tp_integer(  (int)(*(tp_num*)((*++cur).string.val ))  );  // TODO FIXME
			#ifdef DEBUG
				std::cout << RA.integer.val << std::endl;
			#endif
			//cur += sizeof(tp_num)/4;
			//continue;
		} break;

		case TP_INUMBER: {
			#ifdef TP_SANDBOX
			tp_bounds(tp,cur,sizeof(tp_num)/4);
			#endif
			RA = tp_number(*(tp_num*)((*++cur).string.val ));

			#ifdef DEBUG
				std::cout << RA.number.val << std::endl;
			#endif

			cur += sizeof(tp_num)/4;
			continue;
		} break;
		case TP_ISTRING: {
			#ifdef TP_SANDBOX
			tp_bounds(tp,cur,(UVBC/4)+1);
			#endif
			// RA = tp_string_n((*(cur+1)).string.val,UVBC); // from TinyPy - May 13, 2009

			#ifdef DEBUG
				std::cout << "NEW STRING" << std::endl;
				std::cout <<  std::string((*(cur+1)).string.val, UVBC) << std::endl;
			#endif

			//int a = (*(cur+1)).string.val - tp_string_getptr(f->code);
			//RA = tp_string_view(tp, f->code, a, a+UVBC);
			// string_view is NOT broken, but is slightly slower than tp_string_from_const
			RA = tp_string_from_const(tp, (*(cur+1)).string.val, UVBC );


			//if (UVBC <= 5)  // this should work, bug causes some memory error, string becomes a func?
			//	RA = tp_string_atom_from_stdstring(tp, std::string((*(cur+1)).string.val, UVBC) );
			//else
			//	RA = tp_string_from_const(tp, (*(cur+1)).string.val, UVBC );

			cur += (UVBC/4)+1;
			}
			break;

		case TP_IMOVE: RA = RB; break;

		case TP_IIF: if (tp_true(tp,RA)) { cur += 1; } break;
		case TP_IEQ: RA = tp_number(tp_cmp(tp,RB,RC)==0); break;
		case TP_ILE: RA = tp_number(tp_cmp(tp,RB,RC)<=0); break;
		case TP_ILT: RA = tp_number(tp_cmp(tp,RB,RC)<0); break;

		case TP_IGGET: {
			#ifdef DEBUG
				std::cout << "<- TP_IGGET" << std::endl;
				std::cout << "  RA: " << tp_as_string(tp, RA) << std::endl;  // destination register
				std::cout << "  RB: " << tp_as_string(tp, RB) << std::endl;  // name of variable to fetch
			#endif

			if (RB.string.info->len==1) {
				RA = __global_objects__[ (int)RB.string.info->s[0] ];
			} else if (!tp_iget(tp, &RA, f->globals, RB)) {
				RA = tp_get(tp,tp->builtins,RB); GA;
			}
		} break;
		case TP_IGSET: {
			#ifdef DEBUG
				std::cout << "TP_IGSET ->" << std::endl;
				std::cout << "  RA: " << tp_as_string(tp, RA) << std::endl;  // variable name to set to
				std::cout << "  RB: " << tp_as_string(tp, RB) << std::endl;  // value of variable
			#endif

			if (RA.string.info->len==1) {
				//int idx = (int)RA.string.info->s[0];
				//std::cout << "global set index: " << idx << std::endl;
				__global_objects__[ (int)RA.string.info->s[0] ] = RB;
			} else {
				tp_set(tp,f->globals,RA,RB);
			}
		} break;


		case TP_IADD:{
			#ifdef DEBUG
				std::cout << "+ TP_IADD +" << std::endl;
				std::cout << "  RA: " << tp_as_string(tp, RA) << std::endl;  // destination register
				std::cout << "  RB: " << tp_as_string(tp, RB) << std::endl;  // first operand
				std::cout << "  RC: " << tp_as_string(tp, RC) << std::endl;  // second operand
			#endif

			if (RB.type.type_id == TP_NUMBER) {
				RA = tp_number(RB.number.val+RC.number.val);
			} else {
				RA = tp_add(tp,RB,RC);
			}
		}  break;
		case TP_ISUB: RA = tp_sub(tp,RB,RC); break;
		case TP_IMUL: RA = tp_mul(tp,RB,RC); break;
		case TP_IDIV: RA = tp_div(tp,RB,RC); break;


		case TP_ICMP: RA = tp_number(tp_cmp(tp,RB,RC)); break;

		case TP_IMGET: RA = tp_mget(tp,RB,RC); GA; break;
		case TP_IGET: RA = tp_get(tp,RB,RC); GA; break;
		case TP_ISET: tp_set(tp,RA,RB,RC); break;

		case TP_INE: RA = tp_number(tp_cmp(tp,RB,RC)!=0); break;
		case TP_INOT: RA = tp_number(!tp_true(tp,RB)); break;
		case TP_IIFN: if (!tp_true(tp,RA)) { cur += 1; } break;

		case TP_IITER:
			if (RC.number.val < tp_len(tp,RB).number.val) {
				RA = tp_iter(tp,RB,RC); GA;
				RC.number.val += 1;
				#ifdef TP_SANDBOX
				tp_bounds(tp,cur,1);
				#endif
				cur += 1;
			}
			break;

		case TP_IHAS: RA = tp_has(tp,RB,RC); break;
		case TP_IIGET: tp_iget(tp,&RA,RB,RC); break;

		case TP_IDEL: tp_del(tp,RA,RB); break;

		case TP_IIFACE: RA = tp_interface_from_items(tp, VC/2, &RB); break;
		case TP_IDICT: RA = tp_dict_from_items(tp, VC/2, &RB); break;
		case TP_ILIST: RA = tp_list_from_items(tp, VC, &RB); break;
		case TP_IPARAMS: RA = tp_params_n(tp,VC,&RB); break;
		case TP_ILEN: RA = tp_len(tp,RB); break;
		case TP_IJUMP: cur += SVBC; continue; break;
		case TP_ISETJMP: f->jmp = SVBC?cur+SVBC:0; break;
		case TP_ICALL:
			#ifdef TP_SANDBOX
			tp_bounds(tp,cur,1);
			#endif
			f->cur = cur + 1;  RA = tp_call(tp,RB,RC); GA;
			return 0; break;

		case TP_IDEF: {
			#ifdef TP_SANDBOX
			tp_bounds(tp,cur,SVBC);
			#endif
			int a = (*(cur+1)).string.val - tp_string_getptr(f->code);
			if(tp_string_getptr(f->code)[a] == ';') throw "TP_IDEF if(tp_string_getptr(f->code)[a] == ';')";
			RA = tp_def(tp,
				tp_string_view(tp, f->code, a, a + (SVBC-1)*4),
				f->globals);
			cur += SVBC; continue;
			}
			break;
			
		case TP_IRETURN: tp_return(tp,RA); SR(0); break;
		case TP_IRAISE: _tp_raise(tp,RA); SR(0); break;
		case TP_INONE: RA = tp_None; break;


		case TP_IMOD:  RA = tp_mod(tp,RB,RC); break;
		case TP_ILSH:  RA = tp_lsh(tp,RB,RC); break;
		case TP_IRSH:  RA = tp_rsh(tp,RB,RC); break;


		case TP_IPOW: RA = tp_pow(tp,RB,RC); break;
		case TP_IBITAND: RA = tp_bitwise_and(tp,RB,RC); break;
		case TP_IBITOR:  RA = tp_bitwise_or(tp,RB,RC); break;
		case TP_IBITNOT:  RA = tp_bitwise_not(tp,RB); break;
		case TP_IBITXOR:  RA = tp_bitwise_xor(tp,RB,RC); break;

#ifdef DEBUG
		case TP_IPASS: break;

		case TP_IFILE: f->fname = RA; break;

		case TP_IDEBUG:
			tp_echo(tp, tp_string_atom(tp, "DEBUG:"));
			tp_echo(tp, tp_number(VA));
			tp_echo(tp, RA);
			break;

		case TP_ILINE: {
			#ifdef TP_SANDBOX
			tp_bounds(tp,cur,VA);
			#endif
			;
			int a = (*(cur+1)).string.val - tp_string_getptr(f->code);
			if(tp_string_getptr(f->code)[a] == ';') throw "TP_ILINE if(tp_string_getptr(f->code)[a] == ';')";
			f->line = tp_string_view(tp, f->code, a, a+VA*4-1);
			printf("line: %s \n", (*(cur+1)).string.val );

			cur += VA; f->lineno = UVBC;
			}
			break;


		default:{
			printf("INVALID BYTE CODE: %i \n", e.i);
			tp_raise(0,tp_string_atom(tp, "(tp_step) RuntimeError: invalid instruction"));
			break;
		}
#endif
	}  // end of switch

} // end of special cases before switch

	#ifdef TP_SANDBOX
	tp_time_update(tp);
	tp_mem_update(tp);
	tp_bounds(tp,cur,1);
	#endif

	cur += 1;

	}  // end of while
	SR(0);

}


/* Function: tp_exec
 * Execute VM code.
 */
tp_obj tp_exec(TP, tp_obj code, tp_obj globals) {
	tp_obj r = tp_None;
	tp_enter_frame(tp, globals, code, &r);
	tp_run_frame(tp);
	return r;
}

tp_obj tp_eval_from_cstr(TP, const char *text, tp_obj globals) {
	tp_obj code = tp_compile(tp, tp_string_atom(tp, text), tp_string_atom(tp, "<eval>"));
	tp_exec(tp,code,globals);
	return tp->last_result;
}

