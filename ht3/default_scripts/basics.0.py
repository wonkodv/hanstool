"""Populate Env.

This script puts some useful functions into the Env.
"""

from ht3.env import Env

import ht3

from  ht3.command import RESULT_HISTORY as __

from ht3.check import CHECK

from ht3.complete import complete_py
from ht3.complete import complete_all
from ht3.complete import complete_command
from ht3.complete import filter_completions, filter_completions_i
from ht3.complete import complete_path

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

if CHECK.os.windows:
    from ht3.utils.windows import *


def _import():
    import importlib
    for f in ht3.lib.FRONTENDS:
        m = importlib.import_module(f)
        for k in dir(m):
            Env[k] = getattr(m, k)

    import os
    for k, v in os.environ.items():
        if k[:4] == 'HT3_':
            Env[k[4:]] = v

    Env['PATH'] = [Path(p) for p in os.get_exec_path()]

_import()
del _import

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
    try:
        for s in complete_command(string):
            yield s
    except KeyError:
        for s in complete_py(string):
            yield s
