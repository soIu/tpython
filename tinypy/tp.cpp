#include "tp.h"
#include "tp_internal.h"

tp_obj tp_None = {TP_NONE};

#include "tpd_list.cpp"
#include "tpd_dict.cpp"

#include "tp_echo.cpp"
#include "tp_param.cpp"

#include "tp_gc.cpp"
#include "tp_hash.cpp"
#include "tp_list.cpp"
#include "tp_dict.cpp"
#include "tp_string.cpp"

#include "tp_meta.cpp"
#include "tp_frame.cpp"
#include "tp_data.cpp"
#include "tp_func.cpp"

#include "tp_repr.cpp"

#include "tpy_string.cpp"
#include "tpy_dict.cpp"
#include "tpy_list.cpp"

#include "tp_vm.cpp"

/* FIXME: after string / dict gets a meta, register these methods
 * to the meta in tpy_builtin
 * and tp_ops above tpy **/
#include "tp_ops.cpp" 
#include "tp_import.cpp"
#include "tp_interp.cpp"

#ifdef TP_SANDBOX
#include "interp/sandbox.cpp"
#endif


#include "tpy_builtins.cpp"
