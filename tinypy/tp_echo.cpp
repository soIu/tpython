/* File: Miscellaneous
 * Various functions to help interface tinypy.
 */

void tp_echo(TP, tp_obj e) {
    e = tp_str(tp, e);
    tp->echo(tp_string_getptr(e), tp_string_len(e));
}

char * tp_cstr(TP, tp_obj v) {
    char * buffer;
    char const * val;
    if(v.type.type_id != TP_STRING) {
        val = "NOT A STRING";
        buffer = (char*)tp_malloc(tp, strlen(val) + 1);
        memcpy(buffer, val, strlen(val) + 1);
    } else {
        val = tp_string_getptr(v);
        buffer = (char*)tp_malloc(tp, tp_string_len(v) + 1);
        memset(buffer, 0, tp_string_len(v) + 1);
        memcpy(buffer, val, tp_string_len(v));
    }
    
    return buffer;
}

