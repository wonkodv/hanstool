"""Useful bindings that are imported by other scripts

head other scripts with: from Env import *
"""

import os
import os.path
import re
from os.path import expanduser
from pathlib import Path
from time import sleep

import ht3
from ht3 import args
from ht3.check import CHECK
from ht3.command import *
from ht3.complete import *
from ht3.env import Env
from ht3.lib import *
from ht3.utils.dialog import *
from ht3.utils.fake_input import *
from ht3.utils.helpers import *
from ht3.utils.process import *

if CHECK.os.windows:
    from ht3.utils.windows import *



args.Python = args.Param(complete=lambda s: Env.complete_py(s), doc="PythonCode")
args.Path = args.Param(
    convert=pathlib.Path, complete=lambda s: Env.complete_path(s), doc="Path"
)
args.Executable = args.Param(
    complete=lambda s: Env.complete_executable(s), doc="Executable"
)
args.Command = args.Param(complete=lambda s: Env.complete_commands(s), doc="Command")
args.CommandWithArgs = args.Param(
    complete=lambda s: Env.complete_command_with_args(s), doc="CommandWithArgs"
)


Env.update((k, v) for k, v in globals().items() if k[0] != "_")
