import pprint
import sys
from importlib import _bootstrap
from importlib.abc import MetaPathFinder
from types import ModuleType
from typing import Optional, Dict

from dataclasses import dataclass


@dataclass
class ModuleDef:
    name: str
    source: str
    is_package: bool
    file: str


ModuleDefsDict = Dict[str, ModuleDef]


class ModuleImporter(MetaPathFinder):
    _modules_defs: ModuleDefsDict

    @classmethod
    def install(cls, modules: ModuleDefsDict):
        sys.meta_path.insert(0, cls(modules))

    def __init__(self, modules_defs: ModuleDefsDict):
        self._modules_defs = modules_defs

    # Finder part

    def find_spec(self, fullname: str, path, target) -> Optional[_bootstrap.ModuleSpec]:
        if fullname not in self._modules_defs:
            return None

        module_def = self._modules_defs[fullname]
        spec = _bootstrap.spec_from_loader(fullname, self, origin='bundle_lib')
        spec._def = module_def
        return spec

    # Loader part

    def create_module(self, spec):
        spec._code = self.get_code(spec._def.name)

        module = ModuleType(name=spec.name)
        module.__package__ = module.__name__ = spec._def.name
        module.__file__ = spec._def.file
        module.__loader__ = self
        module.__spec__ = spec
        return module

    def exec_module(self, module=None):
        exec(module.__spec__._code, module.__dict__)

    def get_code(self, fullname):
        file = self._modules_defs[fullname].file
        return compile(self.get_source(fullname), file, 'exec')

    def get_source(self, fullname):
        return self._modules_defs[fullname].source or ''

    def is_package(self, fullname):
        return self._modules_defs[fullname].is_package
