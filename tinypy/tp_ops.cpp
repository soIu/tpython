
/* Function: tp_true
 * Check the truth value of an object
 *
 * Returns false if v is a numeric object with a value of exactly 0, v is of
 * type None or v is a string list or dictionary with a length of 0. Else true
 * is returned.
 */
int tp_true(TP,tp_obj v) {
	switch(v.type.type_id) {
		case TP_NUMBER: return v.number.val != 0;
		case TP_NONE: return 0;
		case TP_STRING: return tp_string_len(v) != 0;
		case TP_LIST: return v.list.val->len != 0;
		case TP_DICT: return v.dict.val->len != 0;
	}
	return 1;
}


/* Function: tp_has
 * Checks if an object contains a key.
 *
 * Returns tp_True if self[k] exists, tp_False otherwise.
 */
tp_obj tp_has(TP,tp_obj self, tp_obj k) {
	int type = self.type.type_id;
	if (type == TP_DICT) {
		if (tpd_dict_hashfind(tp, self.dict.val, tp_hash(tp, k), k) != -1) {
			return tp_True;
		}
		return tp_False;
	} else if (type == TP_STRING && k.type.type_id == TP_STRING) {
		return tp_number(tp_str_index(self,k)!=-1);
	} else if (type == TP_LIST) {
		return tp_number(tpd_list_find(tp, self.list.val, k, tp_cmp)!=-1);
	}
	//tp_raise(tp_None,tp_string_atom(tp, "(tp_has) TypeError: iterable argument required"));
	throw "TypeError in tp_ops.cpp:tp_has iterable argument required";
}

/* Function: tp_del
 * Remove a dictionary entry.
 *
 * Removes the key k from self. Also works on classes and objects.
 *
 * Note that unlike with Python, you cannot use this to remove list items.
 */
void tp_del(TP, tp_obj self, tp_obj k) {
	int type = self.type.type_id;
	if (type == TP_DICT) {
		tp_dict_del(tp, self, k);
		return;
	}
	//tp_raise(,tp_string_atom(tp, "(tp_del) TypeError: object does not support item deletion"));
	throw "TypeError in tp_ops.cpp:tp_del object does not support item deletion";
}


/* Function: tp_iter
 * Iterate through a list or dict.
 *
 * If self is a list/string/dictionary, this will iterate over the
 * elements/characters/keys respectively, if k is an increasing index
 * starting with 0 up to the length of the object-1.
 *
 * In the case of a list of string, the returned items will correspond to the
 * item at index k. For a dictionary, no guarantees are made about the order.
 * You also cannot call the function with a specific k to get a specific
 * item -- it is only meant for iterating through all items, calling this
 * function len(self) times. Use <tp_get> to retrieve a specific item, and
 * <tp_len> to get the length.
 *
 * Parameters:
 * self - The object over which to iterate.
 * k - You must pass 0 on the first call, then increase it by 1 after each call,
 *     and don't call the function with k >= len(self).
 *
 * Returns:
 * The first (k = 0) or next (k = 1 .. len(self)-1) item in the iteration.
 */
tp_obj tp_iter(TP,tp_obj self, tp_obj k) {
	int type = self.type.type_id;
	if (type == TP_LIST || type == TP_STRING) { return tp_get(tp,self,k); }
	if (type == TP_DICT && k.type.type_id == TP_NUMBER) {  // hartsantler TODO why is number iterable?
		return self.dict.val->items[tpd_dict_next(tp,self.dict.val)].key;
	}
	//tp_raise(tp_None,tp_string_atom(tp, "(tp_iter) TypeError: iteration over non-sequence"));
	throw "TypeError in tp_ops.cpp:tp_iter iteration over a non-sequence";
}

/* Function: tp_get
 * Attribute lookup.
 * 
 * This returns the result of using self[k] in actual code. It works for
 * dictionaries (including classes and instantiated objects), lists and strings.
 *
 * As a special case, if self is a list, self[None] will return the first
 * element in the list and subsequently remove it from the list.
 */
static tp_obj
_tp_get(TP, tp_obj self, tp_obj k, int mget);

/* lookup using []; never bind functions */
tp_obj tp_get(TP, tp_obj self, tp_obj k) {
	return _tp_get(tp, self, k, 0);
}

/* lookup using .; always bind functions. FIXME: static and class binding */
tp_obj tp_mget(TP, tp_obj self, tp_obj k) {
	return _tp_get(tp, self, k, 1);
}

tp_obj tp_get_by_char(TP, tp_obj d, char c) {
	//std::string s{c};
	//tp_obj key = tp_string_from_stdstring(tp, s);
	tp_obj key = tp_string_from_buffer(tp, (const char*)&c, 1);
	tp_obj item = tp_dict_get(tp, d, key);
	return item;
}
void tp_set_by_char(TP, tp_obj self, char c, tp_obj value) {
	//std::string s{c};
	//tp_obj key = tp_string_from_stdstring(tp, s);
	tp_obj key = tp_string_from_buffer(tp, (const char*)&c, 1);
	tp_dict_set(tp, self, key, value);
}


static tp_obj
_tp_get(TP, tp_obj self, tp_obj k, int mget)
{
	int type = self.type.type_id;
	tp_obj r;
	if (type >= TP_HAS_META) {
		if (type == TP_DICT) {
			/* '.' looks for methods of a raw dict.
			 * [] looks for members */
			if (mget) {
				if (tp_vget(tp, self, k, &r, 1)) {
					return r;
				}
			} else {
				return tp_dict_get(tp, self, k);
			}
		} else if (type == TP_LIST) {
			if (k.type.type_id == TP_NUMBER) {
				int l = tp_len(tp,self).number.val;
				int n = k.number.val;
				n = (n<0?l+n:n);
				return tpd_list_get(tp, self.list.val, n, "tp_get");
			} else if (k.type.type_id == TP_STRING) {
				if (tp_vget(tp, self, k, &r, 1)) { return r;}
			} else if (k.type.type_id == TP_NONE) {
				return tpd_list_pop(tp, self.list.val, 0, "tp_get");
			}
		} else if (type == TP_STRING) {
			if (k.type.type_id == TP_NUMBER) {
				int l = tp_string_len(self);
				int n = k.number.val;
				n = (n<0?l+n:n);
				if (n >= 0 && n < l) { return tp_string_t_from_const(tp, tp->chars[(unsigned char) tp_string_getptr(self)[n]], 1); }
			} else if (k.type.type_id == TP_STRING) {
				if (tp_vget(tp, self, k, &r, 1)) { return r;}
			}
		} else if (type == TP_OBJECT) {
			/* not a raw dict, must be object or interface */
			#ifdef DEBUG
				std::cout << "	begin _tp_get: " << tp_as_string(tp,k) << std::endl;
			#endif
			TP_META_BEGIN(self,"__getitem__");
				return tp_call(tp, meta, tp_params_v(tp, 1, k));
			TP_META_END;
			#ifdef DEBUG
				std::cout << "	falling back to tp_vget" << std::endl;
			#endif

			if (tp_vget(tp, self, k, &r, mget)) {
				#ifdef DEBUG
					std::cout << "	_tp_get OK" << std::endl;
				#endif
				return r;
			}
			#ifdef DEBUG
				std::cout << "	_tp_get failure" << std::endl;
			#endif

		} else if (type == TP_INTERFACE) {
			if (tp_vget(tp, self, k, &r, 0)) {
				return r;
			}
		}
	}
	/* deal with list / string keys on any unknown types */
	if (k.type.type_id == TP_LIST) {
		int a,b,l;
		tp_obj tmp;
		l = tp_len(tp,self).number.val;
		tmp = tp_get(tp,k,tp_number(0));
		if (tmp.type.type_id == TP_NUMBER) { a = tmp.number.val; }
		else if(tmp.type.type_id == TP_NONE) { a = 0; }
		else {
			//tp_raise(tp_None,tp_string_atom(tp, "(tp_get) TypeError: indices must be numbers")); 
			throw "TypeError in tp_ops.cpp:_tp_get indices must be a number";
		}
		tmp = tp_get(tp,k,tp_number(1));
		if (tmp.type.type_id == TP_NUMBER) { b = tmp.number.val; }
		else if(tmp.type.type_id == TP_NONE) { b = l; }
		else {
			//tp_raise(tp_None,tp_string_atom(tp, "(tp_get) TypeError: indices must be numbers")); 
			throw "TypeError in tp_ops.cpp:_tp_get indices must be a number";
		}
		a = _tp_max(0,(a<0?l+a:a)); b = _tp_min(l,(b<0?l+b:b));
		if (type == TP_LIST) {
			return tp_list_from_items(tp,b-a,&self.list.val->items[a]);
		} else if (type == TP_STRING) {
			return tp_string_view(tp,self,a,b);
		}
	} else if (k.type.type_id == TP_STRING) {
		return tp_copy(tp, self);
	}

    std::cout << "_tp_get: self =" << tp_as_string(tp, self) << std::endl;
    std::cout << "_tp_get: key =" << tp_as_string(tp, k) << std::endl;
	//tp_raise(tp_None,tp_string_atom(tp, "(tp_get) TypeError: ?"));
	throw "TypeError in tp_ops.cpp:_tp_get unexpected type";
}

/* function: tp_copy
 * */
tp_obj tp_copy(TP, tp_obj self) {
	int type = self.type.type_id;
	if (type == TP_NUMBER) {
		return self;
	}
	if (type == TP_STRING) {
		return tp_string_from_buffer(tp, tp_string_getptr(self), tp_string_len(self));
	}
	if (type == TP_LIST) {
		return tp_list_copy(tp, self);
	}
	if (type == TP_DICT || type == TP_INTERFACE || type == TP_OBJECT) {
		return tp_dict_copy(tp, self);
	}
	//tp_raise(tp_None, tp_string_atom(tp, "(tp_copy) TypeError: object does not support copy"));
	throw "TypeError in tp_ops.cpp:tp_copy object does not support copy";

}

/* Function: tp_iget
 * Failsafe attribute lookup.
 *
 * This is like <tp_get>, except it will return false if the attribute lookup
 * failed. Otherwise, it will return true, and the object will be returned
 * over the reference parameter r.
 */
int tp_iget(TP,tp_obj *r, tp_obj self, tp_obj k) {
	if (self.type.type_id == TP_DICT || self.type.type_id == TP_OBJECT || self.type.type_id == TP_INTERFACE) {
		int n = tpd_dict_hashfind(tp, self.dict.val, tp_hash(tp, k), k);
		if (n == -1) { return 0; }
		*r = self.dict.val->items[n].val;
		tp_grey(tp,*r);
		return 1;
	}
	if (self.type.type_id == TP_LIST && !self.list.val->len) { return 0; }
	*r = tp_get(tp,self,k); tp_grey(tp,*r);
	return 1;
}

/* Function: tp_set
 * Attribute modification.
 * 
 * This is the counterpart of tp_get, it does the same as self[k] = v would do
 * in actual tinypy code.
 */
void tp_set(TP,tp_obj self, tp_obj k, tp_obj v) {
	int type = self.type.type_id;

	if (type == TP_DICT) {
		tp_dict_set(tp, self, k, v);
		return;
	} else if (type == TP_LIST) {
		if (k.type.type_id == TP_NUMBER) {
			tpd_list_set(tp, self.list.val, k.number.val, v, "tp_set");
			return;
		} else if (k.type.type_id == TP_NONE) {
			tpd_list_append(tp, self.list.val, v);
			return;
		} else if (k.type.type_id == TP_STRING) {
			/* WTF is this syntax? a['*'] = b will extend a by b ??
			 * FIXME: remove this support. Use a + b */
			if (tp_cmp(tp, tp_string_atom(tp, "*"), k) == 0) {
				tpd_list_extend(tp, self.list.val, v.list.val);
				return;
			}
		}
	} else if (type == TP_INTERFACE) {
		tp_dict_set(tp, self, k, v);
		return;
	} else if (type == TP_OBJECT) {
		TP_META_BEGIN(self,"__set__");
			tp_call(tp,meta,tp_params_v(tp,2,k,v));
			return;
		TP_META_END;
		tp_dict_set(tp, self, k, v);
		return;
	}
	//tp_raise(,tp_string_atom(tp, "(tp_set) TypeError: object does not support item assignment"));
	throw "TypeError in tp_ops.cpp:tp_set object does not support item assignment";
}

tp_obj tp_add(TP, tp_obj a, tp_obj b) {
	if (a.type.type_id == TP_NUMBER && a.type.type_id == b.type.type_id) {
		return tp_number(a.number.val+b.number.val);
	} else if (a.type.type_id == TP_STRING && a.type.type_id == b.type.type_id) {
		return tp_string_add(tp, a, b);
	} else if (a.type.type_id == TP_LIST && a.type.type_id == b.type.type_id) {
		return tp_list_add(tp, a, b);
	}
	//tp_raise(tp_None,tp_string_atom(tp, "(tp_add) TypeError: ?"));
	std::cout << "operand A::type_id " << a.type.type_id << std::endl;
	std::cout << "operand B::type_id " << b.type.type_id << std::endl;
	throw "TypeError in tp_ops.cpp:tp_add invalid object type to use the add operator with";
}

tp_obj tp_mul(TP,tp_obj a, tp_obj b) {
	if (a.type.type_id == TP_NUMBER && a.type.type_id == b.type.type_id) {
		return tp_number(a.number.val*b.number.val);
	}
	if(a.type.type_id == TP_NUMBER) {
		tp_obj c = a; a = b; b = c;
	}
	if(a.type.type_id == TP_STRING && b.type.type_id == TP_NUMBER) {
		int n = b.number.val;
		return tp_string_mul(tp, a, n);
	}
	if(a.type.type_id == TP_LIST && b.type.type_id == TP_NUMBER) {
		int n = b.number.val;
		return tp_list_mul(tp, a, n);
	}
	//tp_raise(tp_None,tp_string_atom(tp, "(tp_mul) TypeError: ?"));
	throw "TypeError in tp_ops.cpp:tp_mul invalid object type to use the multiply operator with";
}

/* Function: tp_len
 * Returns the length of an object.
 *
 * Returns the number of items in a list or dict, or the length of a string.
 */
tp_obj tp_len(TP,tp_obj self) {
	int type = self.type.type_id;
	if (type == TP_STRING) {
		return tp_number(tp_string_len(self));
	} else if (type == TP_DICT) {
		return tp_number(self.dict.val->len);
	} else if (type == TP_LIST) {
		return tp_number(self.list.val->len);
	}
	//tp_raise(tp_None,tp_string_atom(tp, "(tp_len) TypeError: len() of unsized object"));
	throw "TypeError in tp_ops.cpp:tp_len invalid object type to use the len function with";
}

int tp_cmp(TP, tp_obj a, tp_obj b) {
	if (a.type.type_id != b.type.type_id) { 
        if (a.type.type_id==TP_INTEGER && b.type.type_id==TP_NUMBER)
            return _tp_sign_int(a.integer.val - (int)b.number.val);
        else if (a.type.type_id==TP_NUMBER && b.type.type_id==TP_INTEGER)
            return _tp_sign_int( (int)a.number.val - b.integer.val);

        //std::cout << "first type: " << a.type.type_id << std::endl;
        //std::cout << "second type: " << b.type.type_id << std::endl;
        //throw "invalid compare of different types";
        return a.type.type_id-b.type.type_id; // why not just return false here?
    }
	switch(a.type.type_id) {
		case TP_NONE: return 0;
		case TP_NUMBER: return _tp_sign(a.number.val-b.number.val);
        case TP_INTEGER: return _tp_sign_int(a.integer.val-b.integer.val);
		case TP_STRING: return tp_string_cmp(a, b);
		case TP_LIST: return tp_list_cmp(tp, a, b);
		case TP_DICT: return a.dict.val - b.dict.val;
		case TP_FUNC: return a.func.info - b.func.info;
		case TP_DATA: return (char*)a.data.val - (char*)b.data.val;
	}
	//tp_raise(0,tp_string_atom(tp, "(tp_cmp) TypeError: ?"));
	throw "TypeError in tp_ops.cpp:tp_cmp invalid object type to compare for equality";
}

tp_obj tp_mod(TP, tp_obj a, tp_obj b) {
	switch(a.type.type_id) {
		case TP_NUMBER:
			if(b.type.type_id == TP_NUMBER)
				return tp_number(((long)a.number.val) % ((long)b.number.val));
			break;
		case TP_STRING:
			return tp_ez_call(tp, "__builtins__", "format", tp_params_v(tp, 2, a, b));
		
	}
	//tp_raise(tp_None, tp_string_atom(tp, "(tp_mod) TypeError: ?"));
	throw "TypeError in tp_ops.cpp:tp_mod invalid object type to use modulus operator with";

}

//tp_raise(tp_None,tp_string_atom(tp, "(" #name ") TypeError: unsupported operand type(s)")); \

#define TP_OP(name,expr) \
	tp_obj name(TP,tp_obj _a,tp_obj _b) { \
	if (_a.type.type_id == TP_NUMBER && _a.type.type_id == _b.type.type_id) { \
		tp_num a = _a.number.val; tp_num b = _b.number.val; \
		return tp_number(expr); \
	} \
	throw "TypeError in tp_ops.cpp unsupported operand type: (" #name ")"; \
}

TP_OP(tp_bitwise_and,((long)a)&((long)b));
TP_OP(tp_bitwise_or,((long)a)|((long)b));
TP_OP(tp_bitwise_xor,((long)a)^((long)b));
TP_OP(tp_lsh,((long)a)<<((long)b));
TP_OP(tp_rsh,((long)a)>>((long)b));
TP_OP(tp_sub,a-b);
TP_OP(tp_div,a/b);
TP_OP(tp_pow,pow(a,b));

tp_obj tp_bitwise_not(TP, tp_obj a) {
	if (a.type.type_id == TP_NUMBER) {
		return tp_number(~(long)a.number.val);
	}
	//tp_raise(tp_None,tp_string_atom(tp, "(tp_bitwise_not) TypeError: unsupported operand type"));
	throw "TypeError tp_ops.cpp:tp_bitwise_not unsupported operand type";
}

/* Function: tp_call
 * Calls a tinypy function.
 *
 * Use this to call a tinypy function.
 *
 * Parameters:
 * tp - The VM instance.
 * self - The object to call.
 * params - Parameters to pass.
 *
 * Example:
 * > tp_call(tp,
 * >     tp_get(tp, tp->builtins, tp_string_atom(tp, "foo")),
 * >     tp_params_v(tp, tp_string_atom(tp, "hello")))
 * This will look for a global function named "foo", then call it with a single
 * positional parameter containing the string "hello".
 */
tp_obj tp_call(TP, tp_obj self, tp_obj params) {
	/* I'm not sure we should have to do this, but
	just for giggles we will. */
	tp->params = params;

	if (self.type.type_id == TP_INTERFACE) {
		tp_obj meta;
		if (tp_vget(tp, self, tp_string_atom(tp, "__new__"), &meta, 1)) {
			tpd_list_insert(tp, params.list.val, 0, self);
			return tp_call(tp, meta, params);
		}
	} else if (self.type.magic == TP_OBJECT) {
		TP_META_BEGIN(self,"__call__");
			return tp_call(tp, meta, params);
		TP_META_END;
	}

	if (self.type.type_id == TP_FUNC) {
		if(!(self.type.magic & TP_FUNC_MASK_C)) {
			if (self.type.magic & TP_FUNC_MASK_METHOD) {
				/* METHOD */
				tpd_list_insert(tp, tp->params.list.val, 0, self.func.info->instance);
			}
			tp_obj (* cfunc)(tp_vm *);
			cfunc = (tp_obj (*)(tp_vm*))self.func.cfnc;

			tp_obj r = cfunc(tp);
			tp_grey(tp, r);
			return r;
		} else {
			/* compiled Python function */
			tp_obj dest = tp_None;
			tp_enter_frame(tp, self.func.info->globals,
							   self.func.info->code,
							  &dest);
			if ((self.type.magic & TP_FUNC_MASK_METHOD)) {
				/* method */
				tp->frames[tp->cur].regs[0] = params;
				tpd_list_insert(tp, params.list.val, 0, self.func.info->instance);
			} else {
				/* function */
				tp->frames[tp->cur].regs[0] = params;
			}
			tp_run_frame(tp);
			return dest;
		}
	}
	//tp_echo(tp, self);
    std::cout << std::endl;
	std::cout << "ERROR in tp_call - object type: " << self.type.type_id << std::endl;
    std::cout << "  object: " << tp_as_string(tp,self) << std::endl;
    std::cout << "  object type: " << self.type.type_id << std::endl;
    std::cout << std::endl;

    std::cout << " The most common cause of this error is the function is undefined," << std::endl;
	std::cout << " in rare cases this error can happen when TP_GCMAX or TP_REGS is not set high enough" << std::endl;
	std::cout << " or when an interface is missing the meta function __new__" << std::endl;
	//tp_raise(tp_None,tp_string_atom(tp, "(tp_call) TypeError: object is not callable"));
	throw "TypeError tp_ops.cpp:tp_call object is not callable";
}

/**/

std::ostream & operator << (std::ostream &out, const tp_obj &self) { 
	out << tp_as_string(NULL, self);
	return out; 
}