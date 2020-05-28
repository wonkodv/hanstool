import ht3
from ht3.env import Env
from ht3 import args
from ht3 import lib
from ht3 import command
from ht3.command import cmd, run_command, COMMANDS
from ht3.utils.helpers import cmd_func


# Raise Errors
@lib.EXCEPTION_HOOK.register
def _raise_error(exception):
    raise exception


SCRIPT_ORDER = ['init']


for k, v in list(vars().items()):
    Env[k] = v
