
import importlib
import unittest
import pybundle.main
from pybundle.stdlib import with_clean_modules, with_clean_path
from dataclasses import asdict
from tests.logger import LogEvent

def _get_globals_from_code(code):
  with with_clean_modules(), with_clean_path():
    ast = compile(code, "code", "exec")
    global_env = {}
    _ = exec(ast, global_env)

  return global_env

def _get_globals_from_path(lib_path):
  with with_clean_modules():
    return vars(importlib.import_module(lib_path))

def _re_class_logs(logs_events):
    # LogEvent objects are from different types.
    # Because they were loaded through different methods.
    return [LogEvent(**asdict(e)) for e in logs_events]



class TestBundleWorks(unittest.TestCase):

  def test_single_file_import(self):
    self._test_import("tests.single_file_import.main")

  def _test_import(self, import_path):
    expected = _get_globals_from_path(import_path)['logs_extractions']

    code = '\n'.join([
      f'from {import_path} import logs_extractions',
    ])
    output_content, _ = pybundle.main.generate_single_main(import_path, code_to_execute = code)
    result = _get_globals_from_code(output_content)['logs_extractions']

    # LogEvent objects are from different types.
    # Because they were loaded through different methods.
    assert expected[0].__class__ is not result[0].__class__

    self.assertListEqual(_re_class_logs(expected), _re_class_logs(result))



if __name__ == '__main__':
    unittest.main()

