import builtins
import contextlib
import dataclasses
import inspect
import os
import sys
import sysconfig
from types import ModuleType
from typing import Dict
import contextlib

from .helpers import ModuleDef, moduleDef_from_module, ModuleDefAndType

BUILTINS = sys.builtin_module_names

KNOWN_STANDARD_LIBRARY = set([
    "abc", "anydbm", "argparse", "array", "asynchat", "asyncore", "atexit", "base64", "BaseHTTPServer", "bisect", "bz2",
    "calendar", "cgitb", "cmd", "codecs", "collections", "commands", "compileall", "ConfigParser", "contextlib",
    "Cookie", "copy", "cPickle", "cProfile", "cStringIO", "csv", "datetime", "dbhash", "dbm", "decimal", "difflib",
    "dircache", "dis", "doctest", "dumbdbm", "EasyDialogs", "errno", "exceptions", "filecmp", "fileinput", "fnmatch",
    "fractions", "functools", "gc", "gdbm", "getopt", "getpass", "gettext", "glob", "grp", "gzip", "hashlib", "heapq",
    "hmac", "imaplib", "imp", "importlib", "inspect", "itertools", "json", "linecache", "locale", "logging", "mailbox",
    "math",
    "mhlib", "mmap", "multiprocessing", "operator", "optparse", "os", "pdb", "pickle", "pipes", "pkgutil", "platform",
    "plistlib", "pprint", "profile", "pstats", "pwd", "pyclbr", "pydoc", "Queue", "random", "re", "readline",
    "resource", "rlcompleter", "robotparser", "sched", "select", "shelve", "shlex", "shutil", "signal",
    "SimpleXMLRPCServer", "site", "sitecustomize", "smtpd", "smtplib", "socket", "SocketServer", "sqlite3", "string",
    "StringIO", "struct", "subprocess", "sys", "sysconfig", "tabnanny", "tarfile", "tempfile", "textwrap", "threading",
    "time", "timeit", "trace", "traceback", "unittest", "urllib", "urllib2", "urlparse", "usercustomize", "uuid",
    "warnings", "weakref", "webbrowser", "whichdb", "xml", "xmlrpclib", "zipfile", "zipimport", "zlib", 'builtins',
    '__builtin__'
])

KNOWN_STANDARD_LIBRARY_THE_RETURN = set([
    'tty',
    'termios',
])


def get_std_lib():
    # For python 10, use sys.stdlib_module_names
    res = set()
    sysconfig.get_path_names()
    std_lib = sysconfig.get_python_lib(standard_lib=True)
    for top, dirs, files in os.walk(std_lib):
        for nm in files:
            if nm != '__init__.py' and nm[-3:] == '.py':
                res.add(os.path.join(top, nm)[len(std_lib) + 1:-3].replace(os.sep, '.'))
    return res



def can_be_removed(loaded_module):
  """Tell us if a module can be removed from sys.modules"""
  # TODO : is there a better way of doing that ?
  r, n, f = str(loaded_module), loaded_module.__name__, str(getattr(loaded_module, '__file__', None))
  if '(built-in)' in r:
    return False
  if f.startswith(sys.base_prefix):
    return False
  if n == '__main__':
    return False
  return True

def is_import_to_keep(fullname: str, module: ModuleType) -> bool:
    if fullname in KNOWN_STANDARD_LIBRARY:
        return False
    if fullname in KNOWN_STANDARD_LIBRARY_THE_RETURN:
        return False
    # We're mean here to remove everything that is not proper for py files.
    # so, pyc, frozenmodules, etc...
    return True




class GetImportsThatHasBeenAdded:
    _modules_imported: Dict[str, ModuleDefAndType]

    def __init__(self):
        self._modules_imported = {}

    @property
    def modules_imported(self) -> Dict[str, ModuleDefAndType]:
        return self._modules_imported.copy()

    @staticmethod
    def module_to_dataclass(name: str, module: ModuleType) -> ModuleDef:
        return ModuleDef(
            name=name,
            code=inspect.getsource(module),
            is_package=True,
        )

    @contextlib.contextmanager
    def catch_imports(self, autoclean=True) -> None:
        existing_names = set(sys.modules.keys())
        try:
            yield self
        finally:
            self._modules_imported = {
                name: ModuleDefAndType(moduleDef_from_module(module), sys.modules[name])
                for name, module in sys.modules.items()
                if name not in existing_names and is_import_to_keep(name, module)
            }

            if autoclean:
                for name in self._modules_imported.keys():
                    del sys.modules[name]
                    
@contextlib.contextmanager
def with_clean_modules():
  # Execute the code keeping only build-in modules.
  modules_copy = sys.modules.copy()
  for key, value in list(sys.modules.items()):
    if can_be_removed(value):
      del sys.modules[key]        
  try:
    yield None
  finally:
    sys.modules.update(modules_copy)

@contextlib.contextmanager
def with_clean_path():
  path_copy = list(sys.path)
  sys.path[:] = [p for p in sys.path if p.startswith(sys.base_prefix)]
  try:
    yield None
  finally:
    sys.path[:] = path_copy


