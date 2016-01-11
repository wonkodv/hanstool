"""Populate Env.

This script puts some useful functions into the Env.
"""


import ht3

from  ht3.command import RESULT_HISTORY as __

from ht3.check import CHECK

from ht3.complete import complete_all
from ht3.complete import complete_py
from ht3.complete import complete_command
from ht3.complete import filter_completions

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
if CHECK.os.windows:
    from ht3.utils.windows import *

from ht3.utils.fake_input import *
from ht3.utils.handler import *
from ht3.utils.process import *
from ht3.utils.helpers import *
from ht3.utils.log import *

def _():
    import importlib
    for f in ht3.lib.FRONTENDS:
        m = importlib.import_module(f)
        for k in dir(m):
            Env[k] = getattr(m, k)

    import os
    for k, v in os.environ.items():
        if k[:4] == 'HT3_':
            Env[k[4:]] = v

_()
