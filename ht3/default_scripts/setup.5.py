from Env import *

from ht3.command import COMMAND_RESULT_HOOK


Env['__'] = []
Env['_'] = None

@COMMAND_RESULT_HOOK.register
def _command_results(command):
    Env['__'].append(command.result)
    if command.result is not None:
        Env['_'] = command.result
