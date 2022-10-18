import ast

import astunparse
#import autopep8


def codecleaner(code_str: str) -> str:
    """Get a string representing code as parameter and return cleaned verion of it."""
    ast.parse(code_str)  # This should throw exception if code is not valid.
    return code_str


def codeobfuscation(code_str: str) -> str:
    """TODO : to fill, but for later."""
    #return autopep8.fix_code(code_res_str, options={'aggressive': 1})
    pass
