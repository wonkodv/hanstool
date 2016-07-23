"""Useful bindings that are imported by other scripts

head other scripts with: from Env import *
"""


import ht3

# import b real path in case it was not included before (can not happen ?)
from ht3.env import Env

from ht3.check import CHECK

from ht3 import args

from time import sleep
from os.path import expanduser
from pathlib import Path

from ht3.command import *
from ht3.lib import *

from ht3.utils.fake_input import *
from ht3.utils.process import *
from ht3.utils.helpers import *
from ht3.utils.dialog import *

from ht3.complete import *

if CHECK.os.windows:
    from ht3.utils.windows import *

# Put all above bindings into Env
Env.dict.update(vars())
