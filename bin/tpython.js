#!/usr/bin/env node
var os = require('os');
var fs = require('fs');
var path = require('path');
var process = require('process');
var child_process = require('child_process');
var tpython = path.join(__dirname, '../rebuild.py');
var tpydir = path.join(tpython, '../')
var platform = os.platform();

//process.env.TPY_USE_EMSCRIPTEN = 'true';

function check_exist(command, dont_append_version) {
  try {
    child_process.execSync(command + (dont_append_version ? '' : ' --version'), {stdio: 'ignore'});
    return true;
  }
  catch (error) {
    return false;
  }
}

/*function cygpath(fullpath) {
  return child_process.execSync("cygpath '" + fullpath + "'").toString().trim();
}*/

/*if (platform === 'win32') {
  if (!check_exist('cygpath')) {
    throw new Error("Currently the only possible way to compile WASM TPython programs on Windows is with Cygwin, make sure to install python2.7, gcc-core and make on the Cygwin installer. And delete /usr/bin/python on Cygwin (It interferes with emscripten's Python 3)");
  }
  tpython = cygpath(tpython);
}*/


var use_wasm = process.argv.indexOf('--wasm') !== -1;

var emcc = platform === 'win32' ? 'em++.bat' : 'em++';
var python = 'python3'; //'pypy';
/*if (!check_exist('pypy')) {
  python = 'python2.7';
  if (!check_exist('python2.7')) throw new Error('PyPy (pypy not pypy3) or Python 2.7 (python2.7) must be installed and exist on PATH');
}*/
if (!check_exist('make -v', true)) throw new Error('make (usually comes from build-essential, or just install the standalone package) must be installed and exist on PATH');
//if (!check_exist('gcc -v', true)) console.error('GCC (gcc) is somewhat needed, but not necessary');
if (!check_exist(emcc + ' -v', true)) throw new Error('em++ (comes with emsdk) must be installed and exist on PATH');
/*var tempdir = path.join(os.tmpdir(), 'tpython-' + (new Date()).getTime());
fs.mkdirSync(tempdir);*/
//process.env.TPYTHON_TARGET_FILE = process.argv[2];
//process.env.PYPY_USESSION_DIR = platform === 'win32' ? cygpath(tempdir) : tempdir;
//process.env.USER = 'current';
const additional_args = [];
if (!use_wasm) additional_args.push('--wasmjs');
additional_args.push('--html')
child_process.execSync([python, tpython].concat(additional_args).concat(process.argv.slice(2)).join(' '), {stdio: 'inherit', env: process.env, cwd: tpydir});
