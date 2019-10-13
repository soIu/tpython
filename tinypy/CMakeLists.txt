cmake_minimum_required(VERSION 3.8)

#set(CMAKE_C_COMPILER /usr/bin/clang-6.0)
#set(CMAKE_CXX_COMPILER /usr/bin/clang++-6.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_definitions(-DINCLUDEOS -DUSE_EMBEDDED_BYTECODE -DEBUG)

set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
project (tinypy)
include(${CMAKE_CURRENT_BINARY_DIR}/conanbuildinfo.cmake OPTIONAL RESULT_VARIABLE HAS_CONAN)
conan_basic_setup()
include(os)

os_add_executable(tpythonos "TPythonOS" tp.cpp dummy-compiler.cpp runtime.cpp vmmain.cpp)
#os_add_drivers(tpythonos virtionet vmxnet3 boot_logger)
os_add_stdout(tpythonos default_stdout)
