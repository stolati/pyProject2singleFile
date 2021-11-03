
import importlib
import unittest
import pybundle.main
from pybundle.stdlib import with_clean_modules, with_clean_path
import pprint
from dataclasses import asdict
from tests.logger import LogEvent


import_path = 'tests.single_file_import.main'

class TestBundleWorks(unittest.TestCase):

  def test_upper(self):

    code = '\n'.join([
      f'from {import_path} import logs_extractions',
    ])

    expected = importlib.import_module(import_path).logs_extractions

    output_content, modules = pybundle.main.generate_single_main(import_path, code_to_execute = code)
    
    with with_clean_modules(), with_clean_path():
      ast = compile(output_content, "code", "exec")
      global_env = {}
      exec_r = exec(ast, global_env)

    result = global_env['logs_extractions']

    # LogEvent objects are form different types
    assert expected[0].__class__ is not result[0].__class__

    expected = [LogEvent(**asdict(e)) for e in expected]
    result = [LogEvent(**asdict(e)) for e in result]
    self.assertListEqual(expected, result)


if __name__ == '__main__':
    unittest.main()

