from Env import *

from ht3.env import Env
import os
from pathlib import Path
from ht3.command import COMMAND_RESULT_HOOK


### Get OS Variables

for k, v in os.environ.items():
    if k[:4] == 'HT3_':
        Env[k[4:]] = v

Env['PATH'] = [Path(p) for p in os.get_exec_path()]


__=[]
_=None

@COMMAND_RESULT_HOOK.register
def _command_results(result, **kwargs):
    global __
    global _
    __.append(result)
    if result is not None:
        _ = result
