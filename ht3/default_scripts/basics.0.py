"""Populate Env.

This script puts some useful functions into the Env.
"""

from ht3.env import Env

import ht3

from  ht3.command import RESULT_HISTORY as __

from ht3.check import CHECK

from ht3 import args

from ht3.command import cmd
from ht3.command import COMMANDS
from ht3.command import run_command

from ht3.lib import evaluate_py_expression
from ht3.lib import execute_py_expression
from ht3.lib import start_thread

from time import sleep
from os.path import expanduser
from pathlib import Path

from ht3.check import CHECK

from ht3.utils.fake_input import *
from ht3.utils.process import *
from ht3.utils.helpers import *
from ht3.utils.log import *
from ht3.utils.dialog import *

from ht3.complete import *

if CHECK.os.windows:
    from ht3.utils.windows import *

@run
def _import():
    import importlib
    excludes = ['start', 'loop', 'stop']
    for f in ht3.lib.FRONTENDS:
        m = importlib.import_module(f)
        if hasattr(m, '__all__'):
            for k in m.__all__:
                Env[k] = getattr(m, k)
        else:
            for k in set(dir(m)):
                if k[0] != '_' and k not in excludes:
                    Env[k] = getattr(m, k)

    import os
    for k, v in os.environ.items():
        if k[:4] == 'HT3_':
            Env[k[4:]] = v

    Env['PATH'] = set(Path(p) for p in os.get_exec_path())

def error_hook(e):
    global _LAST_ERROR
    _LAST_ERROR = e
    log_error(e)

def command_not_found_hook(s):
    """ Try to evaluate as expression and return the result,
        if that fails, execute as statements """
    try:
        return evaluate_py_expression(s)
    except SyntaxError:
        pass
    execute_py_expression(s)

def general_completion(string):
    """General completion.

    Complete command-strings that the user enters, including stuff that the
    command_not_found_hook will get. Specifically, complete commands but if
    none matched complete python."""

    p_space = string.find(' ')
    p_paren = string.find('(')

    if p_space == -1:
        if p_paren == -1:
            #ABC
            return ht3.complete.complete_commands(string)
        else:
            #AB(C
            return ht3.complete.complete_py(string)
    else:
        if p_paren == -1:
            #AB C
            return ht3.complete.complete_command_args(string)
        else:
            if p_paren < p_space:
                #ab( c)
                return ht3.complete.complete_py(string)
            else:
                #a b(c)
                return ht3.complete.complete_command_args(string)

CommandOrExpression = args.Param(complete=general_completion, doc="CommandOrExpression")
