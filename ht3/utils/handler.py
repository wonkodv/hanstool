"""Default handler."""

from ht3.env import Env
from ht3.lib import execute_py_expression, evaluate_py_expression
import warnings

def command_not_found_hook(s):
    """ Try to evaluate as expression and return the result,
        if that fails, execute as statements """
    try:
        return evaluate_py_expression(s)
    except SyntaxError:
        pass
    execute_py_expression(s)
