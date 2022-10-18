import inspect
from types import ModuleType
from typing import Dict, Tuple

from . import export as bundle_export
from .helpers import load_file_as_module, ModuleDefAndType, load_name_as_module
from .stdlib import GetImportsThatHasBeenAdded, with_clean_modules
from .export import ModuleImporter, ModuleDef
from .codecleaner import codecleaner


ModuleDict = Dict[str, Tuple[ModuleDef, ModuleType]]

def get_modules_imported_from_file(file_path, module_name='_main_') -> ModuleDict:
  gi_added = GetImportsThatHasBeenAdded()

  with with_clean_modules(), gi_added.catch_imports() as mobdules_imported:
    moduledefandtype = load_file_as_module(file_path, module_name)

  modules_imported = gi_added.modules_imported.copy()
  modules_imported['_main_'] = moduledefandtype

  return modules_imported

def get_modules_imported_from_import(module_name) -> ModuleDict:
  gi_added = GetImportsThatHasBeenAdded()

  with with_clean_modules(), gi_added.catch_imports() as mobdules_imported:
    moduledefandtype = load_name_as_module(module_name)

  modules_imported = gi_added.modules_imported.copy()
  modules_imported[moduledefandtype.module_def.name] = moduledefandtype

  return modules_imported



def create_fake_modules(module_names) -> Dict[str, ModuleDefAndType]:
    res = {}
    for module_name in module_names:
        module_def = ModuleDef(
            name=module_name,
            source="# Fake module",
            is_package=True,
            file=module_name.replace('.', '/') + '.py',
        )

        res[module_name] = ModuleDefAndType(module_def, None)
    return res


def _pprint_modules(input: Dict[str, ModuleDefAndType], variable_name: str) -> str:
    def create_source_var_name(module):
        return 'MODULE_' + module.name.upper().replace('.', '_') + '_SOURCE'

    extract_sources = sorted([
        f'{create_source_var_name(mdt.module_def)} = {mdt.module_def.source!r}' for mdt in input.values()
    ])

    modules_defs = sorted([
        f'    {k!r}: ModuleDef(name={mdt.module_def.name!r}, '
        f'file={mdt.module_def.file!r}, '
        f'is_package={mdt.module_def.is_package!r}, '
        f'source={create_source_var_name(mdt.module_def)}),'
        for k, mdt in input.items()
    ])

    lines = extract_sources + ['', variable_name + ' = {'] + modules_defs + ['}']

    return '\n'.join(lines)

def get_python_exec():
  return 'python3.8'  # TODO use sys.version_info

def generate_single_main(
  module_name: str,
  is_module_main: bool = False,
  code_to_execute: str = '',
  fake_modules=[],
  python_exec = None,
  ) -> Tuple[str, ModuleDict]:
    # TODO : handle is_module_main

    modules = get_modules_imported_from_import(module_name)

    fake_modules = create_fake_modules(fake_modules)

    modules = dict(**modules, **fake_modules)

    export = inspect.getsource(bundle_export)

    output_lines = [
        f"#!/usr/bin/env {get_python_exec()}",
        export,
        _pprint_modules(modules, 'MODULES_DEFS'),
        f'ModuleImporter.install(MODULES_DEFS)',
        code_to_execute,
    ]

    # Debug statement
    output_text = '\n\n'.join(output_lines)

    #print(code_with_lines(output_text))

    output_content = codecleaner(output_text)
    #print(code_with_lines(output_content))
    return output_content, modules


def code_with_lines(code):
    return '\n'.join(
      f'L{i+1}  {l}' for i, l in enumerate(code.split('\n'))
    )


