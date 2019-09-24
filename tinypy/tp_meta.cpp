int _tp_lookup_(TP, tp_obj self, int hash, tp_obj k, tp_obj *member, int bind, int depth) {

    tp_obj meta;

    if (self.type.type_id < TP_HAS_META) {
        return 0;
    } else {
        meta = self.obj.info->meta;
    }

    /* if we land on a class, try to find the member directly */
    if(self.type.type_id == TP_INTERFACE) {
        /* first do a dict look up from the object itself */
        int n = tpd_dict_hashfind(tp, self.dict.val, hash, k);
        if (n != -1) {
            *member = self.dict.val->items[n].val;
            return 1;
        }
    }

    /* no meta */
    if (meta.type.type_id == TP_NONE) {
        return 0;
    }

    if (depth == 8) {
        //tp_raise(0,tp_string_atom(tp, "(tp_lookup) RuntimeError: maximum lookup depth exceeded"));
        throw "RuntimeError in tp_meta.cpp: maximum lookup depth exceeded";
    }
    
    if (meta.type.type_id != TP_INTERFACE) {
        //tp_raise(0,tp_string_atom(tp, "(tp_lookup) RuntimeError: meta is neither an interface nor None"));
        throw "RuntimeError in tp_meta.cpp: meta is neither an interface nor None";
    }

    /* nested lookup always bind */
    int nextbind = 1;
    if (_tp_lookup_(tp, meta, hash, k, member, nextbind, depth + 1)) {
        /* bind as a member ? */
        if (!bind) return 1;

        /* FIXME: this will unbind the existing binding. should have nested. */
        if ( member->type.type_id == TP_FUNC) {
            /* an object is seen, bind the meta method to the instance */
            /* object, dict or string, or list */
            if (   self.type.type_id == TP_DICT
                || self.type.type_id == TP_LIST
                || self.type.type_id == TP_STRING
                || self.type.type_id == TP_OBJECT
            ) {
                *member = tp_bind(tp, *member, self);
            }
        }
        return 1;
    }
    return 0;
}

int tp_vget(TP, tp_obj self, tp_obj k, tp_obj * member, int bind) {
    return _tp_lookup_(tp, self, tp_hash(tp, k), k, member, bind, 0);
}

#define TP_META_BEGIN(self,name) \
    if ((self.type.type_id == TP_DICT || self.type.type_id == TP_OBJECT) || \
        (self.type.type_id == TP_STRING || self.type.type_id == TP_LIST ) \
        ) { \
        tp_obj meta; if (tp_vget(tp, self, tp_string_atom(tp, name), &meta, 1)) {
#define TP_META_END \
        } \
    }

