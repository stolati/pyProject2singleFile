import inspect
import pprint
import sys
import textwrap
from types import ModuleType
from typing import Dict, Tuple

import autopep8

import pybundle
from pybundle.helpers import load_file_as_module, ModuleDefAndType
from pybundle.stdlib import GetImportsThatHasBeenAdded
from pybundle.export import ModuleImporter, ModuleDef
from pybundle.codecleaner import codecleaner


def get_modules_imported_from_file(file_path, module_name='_main_') -> Dict[str, Tuple[ModuleDef, ModuleType]]:
    gi_added = GetImportsThatHasBeenAdded()

    with gi_added.catch_imports():
        moduledefandtype = load_file_as_module(file_path, module_name)

    modules_imported = gi_added.modules_imported.copy()
    modules_imported['_main_'] = moduledefandtype

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

    lines = extract_sources + ['', f'{variable_name} = {{'] + modules_defs + ['}']

    return '\n'.join(lines)


def generate_single_main(import_path: str, code_to_execute: str = '', fakes=[]) -> None:
    modules = get_modules_imported_from_file(file_path)
    fake_modules = create_fake_modules(fakes)

    modules = dict(**modules, **fake_modules)

    export = inspect.getsource(bundle.export)

    output_lines = [
        "#!/usr/bin/env python3.8",
        export,
        _pprint_modules(modules, 'MODULES_DEFS'),
        f'ModuleImporter.install(MODULES_DEFS)',
        code_to_execute,
    ]

    output_content = codecleaner('\n\n'.join(output_lines))

    with open(output_file, 'w') as f:
        f.write(output_content)

    return modules
