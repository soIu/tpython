#include <iostream>

typedef struct {
    char * buffer;
    int size;
    int len;
} StringBuilder;

void string_builder_write (TP, StringBuilder * sb, const char * s, int len)
{
    if(len < 0) len = strlen(s);
    if(sb->len + len + 1 >= sb->size) {
        sb->size = (sb->len + len + 1) + sb->len / 2;
        sb->buffer = (char*)tp_realloc(tp, sb->buffer, sb->size);
    }
    memcpy(sb->buffer + sb->len, s, len);
    sb->len += len;
    sb->buffer[sb->len] = 0;
}

void tp_str_(TP, tp_obj self, tpd_list * visited, StringBuilder * sb, int mode);


tp_obj tp_str_internal_DEPRECATED(TP, tp_obj self, int mode) {
    /* we only put unmanaged tp_data objects to the list.*/
    tpd_list * visited = tpd_list_new(tp);
    StringBuilder sb[1];
    sb->buffer = (char*)tp_malloc(tp, 128);
    sb->len = 0;
    sb->size = 128;

    tp_str_(tp, self, visited, sb, mode);

    tpd_list_free(tp, visited);
    /* FIXME: add API to steal a buffer to form a string. */
    tp_obj r = tp_string_from_buffer(tp, sb->buffer, sb->len);
    tp_free(tp, sb->buffer);
    return r;
}

std::string tp_str_internal(TP, tp_obj self) {
    std::stringstream ss;
    int type = self.type.type_id;
    switch( type ) {
        case TP_STRING: ss << "\"" << self.string.val << "\""; break;
        case TP_NUMBER: ss << self.number.val; break;
        case TP_NONE: ss << "None"; break;
        case TP_FUNC: ss << "function<" << self.func.cfnc << ">"; break;
        case TP_LIST: {
            ss << "[";
            for (int i=0; i<self.list.val->len; i++){
                ss << tp_str_internal(tp, self.list.val->items[i]) << ",";
            }
            ss << "]";
        } break;
        case TP_DICT: {
            ss << "{";
            for (int i=0; i<self.dict.val->len; i++){
                tpd_item item = self.dict.val->items[i];
                ss << tp_str_internal(tp, item.key) << ":";
                ss << tp_str_internal(tp, item.val);
                ss << ",";
            }
            ss << "}";
        } break;
        case TP_OBJECT: {
            ss << "object<" << self.object.val << ">";
        } break;
        case TP_INTERFACE: {
            ss << "interface<" << self.interface.val << ">";
        } break;
        case TP_DATA: {
            ss << "data<" << self.data.val << ">";
        } break;
        default:
            ss << "<unknown type>";

    }

    return ss.str();
}

tp_obj tp_str(TP, tp_obj self) {
    return tp_string_from_stdstring(tp, tp_str_internal(tp, self));
}
tp_obj tp_repr(TP, tp_obj self) {
    return tp_string_from_stdstring(tp, tp_str_internal(tp, self));
}

/* Function: tp_str
 * String representation of an object.
 * Checks for recursive data structures
 *
 * Returns a string object representating self.
 */
void tp_str_(TP, tp_obj self, tpd_list * visited, StringBuilder * sb, int mode) {
    /* if the class has __str__ or __repr__ use those */
    if(mode != 0) { /* str mode */
        TP_META_BEGIN(self,"__str__");
            tp_obj obj = tp_call(tp, meta, tp_params(tp));
            string_builder_write(tp, sb, tp_string_getptr(obj), tp_string_len(obj));
            return;
        TP_META_END;
    }
    TP_META_BEGIN(self,"__repr___");
        tp_obj obj = tp_call(tp, meta, tp_params(tp));
        string_builder_write(tp, sb, tp_string_getptr(obj), tp_string_len(obj));
        return;
    TP_META_END;

    int type = self.type.type_id;


/*
    if(type == TP_DICT || type == TP_INTERFACE || type == TP_OBJECT) {
        tp_obj data = tp_data_nt(tp, 0, self.dict.val);
        // FIXME: use tp_data_cmp
        if(tpd_list_find(tp, visited, data, tp_cmp) >= 0) {
            string_builder_write(tp, sb, "{...}", -1);
            return;
        }
        tpd_list_append(tp, visited, data);
        printf("pushing-dict-inter-ob %d %p\n", visited->len, self.dict.val);
    } else if(type == TP_LIST) {
        tp_obj data = tp_data_nt(tp, 0, self.list.val);
        if(tpd_list_find(tp, visited, data, tp_cmp) >= 0) {
            string_builder_write(tp, sb, "[...]", -1);
            return;
        }
        tpd_list_append(tp, visited, data);
        printf("pushing-list %d %p\n", visited->len, self.list.val);
    }
*/

    if (type == TP_STRING) { 
        if(mode != 0) { /* str */
            string_builder_write(tp, sb, tp_string_getptr(self), tp_string_len(self));
        } else { /* repr */
            int i;
            string_builder_write(tp, sb, "'", 1);
            for (i = 0; i < tp_string_len(self); i ++) {
                const char * s = tp_string_getptr(self) + i;
                switch(s[0]) {
                    case '\n':
                        string_builder_write(tp, sb, "\\n", 2);
                        break;
                    case '\r':
                        string_builder_write(tp, sb, "\\r", 2);
                        break;
                    case '\t':
                        string_builder_write(tp, sb, "\\t", 2);
                        break;
                    case '\'':
                    case '\"':
                        string_builder_write(tp, sb, "\\", 1);
                    /* leak through */
                    default:
                        string_builder_write(tp, sb, s, 1);
                }
            }
            string_builder_write(tp, sb, "'", 1);
        } 
    } else if (type == TP_NUMBER) {

        // DEPRECATED because the size of tp_num can vary
        /*
        char buf[128];
        tp_num v = self.number.val;
        if ((fabs(v-(long)v)) < 0.000001) {
            snprintf(buf, 120, "%ld", (long)v);
            string_builder_write(tp, sb, buf, -1);
        } else {
            snprintf(buf, 120, "%f", v);
        }
        */
        std::cout << self.number.val << std::endl;

    } else if(type == TP_DICT || type == TP_INTERFACE || type == TP_OBJECT) {
        string_builder_write(tp, sb, "{", -1);
        int i, n = 0;
        for(i = 0; i < self.dict.val->alloc; i++) {
            if(self.dict.val->items[i].used > 0) {
                tp_str_(tp, self.dict.val->items[i].key, visited, sb, mode);
                string_builder_write(tp, sb, ": ", -1);
                tp_str_(tp, self.dict.val->items[i].val, visited, sb, mode);
                if(n < self.dict.val->len - 1) {
                    string_builder_write(tp, sb, ", ", -1);
                }
                n += 1;
            }
        }
        string_builder_write(tp, sb, "}", -1);
    } else if(type == TP_LIST) {
        string_builder_write(tp, sb, "[", -1);
        int i;
        for(i = 0; i < self.list.val->len; i++) {
            tp_str_(tp, self.list.val->items[i], visited, sb, mode);
            if(i < self.list.val->len - 1) {
                string_builder_write(tp, sb, ", ", -1);
            }
        }
        string_builder_write(tp, sb, "]", -1);
    } else if (type == TP_NONE) {
        string_builder_write(tp, sb, "None", -1);
    } else if (type == TP_DATA) {
        char buf[128];
        // blendot fixes sept20th
        //snprintf(buf, 120, "<data 0x%x>", self.data.val);
        snprintf(buf, 120, "<data 0x%lx>", (unsigned long)self.data.val);
        string_builder_write(tp, sb, buf, -1);
    } else if (type == TP_FUNC) {
        char buf[128];
        // blendot fixes sept20th
        //snprintf(buf, 120, "<func 0x%x>", self.func.info);
        snprintf(buf, 120, "<func 0x%lx>", (unsigned long)self.func.info);
        string_builder_write(tp, sb, buf, -1);
    } else {
        string_builder_write(tp, sb, "<?>", -1);
    }
    if(type == TP_DICT || type == TP_LIST || type == TP_INTERFACE || type == TP_OBJECT) {
        printf("poping, %d %p %p\n", visited->len, self.dict.val, self.list.val);
        tpd_list_pop(tp, visited, visited->len - 1, "visited list is empty");
    }
    return;
}

