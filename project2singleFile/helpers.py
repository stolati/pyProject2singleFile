# Decorator to print function call
# details
import dataclasses
import inspect
import os.path
import subprocess
import sys
import tempfile
from importlib.machinery import SourceFileLoader
from types import ModuleType
from typing import List, Tuple
import importlib

# Keep it for other to access it
from project2singleFile.export import ModuleDef


@dataclasses.dataclass(frozen=True)
class ModuleDefAndType:
    module_def: ModuleDef
    module_type: ModuleType


def clear_modules(list_prefix: List[str]):
    for name in list_prefix:
        for key in list(sys.modules.keys()):
            if key.startswith(name):
                del sys.modules[key]


def remove_local_path(path):
    if os.path.isfile(path):
        path = os.path.dirname(path)
    sys.path = [p for p in sys.path if not p.startswith(path)]



def moduleDef_from_module(module: ModuleType):
    is_package = module.__name__ == module.__package__
    name = module.__name__

    try:
        source = inspect.getsource(module)
    except:
        source = ''

    name_path = name.replace('.', '/')
    if is_package:
        file = f'{name_path}/__init__.py'
    else:
        file = f'{name_path}.py'

    return ModuleDef(
        name=name,
        source=source,
        is_package=is_package,
        file=file,
    )


def load_file_as_module(file_path, module_name) -> Tuple[ModuleDefAndType]:
    module_inst = SourceFileLoader(module_name, file_path).load_module()
    return ModuleDefAndType(moduleDef_from_module(module_inst), module_inst)

def load_name_as_module(module_name) -> Tuple[ModuleDefAndType]:
  module_inst = importlib.import_module(module_name)
  return ModuleDefAndType(moduleDef_from_module(module_inst), module_inst)


def call_python_on_file(file_path):
    """Helper to execute a python without current local context."""

    with open(file_path, 'rb') as origin, \
            tempfile.NamedTemporaryFile(suffix='.main.py') as temp_file:
        temp_file.write(origin.read())
        temp_file.flush()

        environ = {k: v for k, v in os.environ.items() if 'PYTHON' not in k}

        subprocess.check_call(
            [sys.executable, temp_file.name],
            cwd='/',
            env=environ,
        )

