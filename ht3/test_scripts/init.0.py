from ht3.command import cmd, run_command, COMMANDS
from ht3.env import Env
from ht3 import args
from ht3 import lib
from ht3 import command

@lib.EXCEPTION_HOOK.register
@command.COMMAND_EXCEPTION_HOOK.register
def _raise_error(exception, **k):
    raise exception
