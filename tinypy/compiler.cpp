#include "tp.h"

#include "compiler/boot.cpp"
#include "compiler/encode.cpp"
#include "compiler/parse.cpp"
#include "compiler/tokenize.cpp"
#include "compiler/py2bc.cpp"

void tp_module_compiler_init(TP) {
    tp_import_from_buffer(tp, 0, "tinypy.compiler.boot", _tp_boot_tpc,  sizeof(_tp_boot_tpc));
    tp_import_from_buffer(tp, 0, "tinypy.compiler.tokenize", _tp_tokenize_tpc,  sizeof(_tp_tokenize_tpc));
    tp_import_from_buffer(tp, 0, "tinypy.compiler.parse", _tp_parse_tpc, sizeof(_tp_parse_tpc));
    tp_import_from_buffer(tp, 0, "tinypy.compiler.encode", _tp_encode_tpc, sizeof(_tp_encode_tpc));
    tp_import_from_buffer(tp, 0, "tinypy.compiler.py2bc", _tp_py2bc_tpc, sizeof(_tp_py2bc_tpc));
}
