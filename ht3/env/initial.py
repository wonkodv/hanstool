from . import Env
Env.__ = []
Env._  = None



import os
for k, v in os.environ.items():
    if k[:4] == 'HT3_':
        Env[k[4:]] = v

import time
Env(time.sleep)

from ht3.complete import complete_all, complete_py, complete_command
Env(complete_py)
Env(complete_command)
Env(complete_all)

from ht3.command import cmd, COMMANDS, run_command
Env(cmd)
Env.COMMANDS = COMMANDS
Env(run_command)

from ht3.lib import Check, evaluate_py_expression, execute_py_expression, start_thread
Env.Check = Check
Env(evaluate_py_expression)
Env(execute_py_expression)
Env(start_thread)

from . import log
from . import handler
from . import fake_input
from . import process
from . import helpers

if Check.os.windows:
    from . import windows
