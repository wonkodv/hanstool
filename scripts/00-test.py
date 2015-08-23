from ht3.cmd import cmd
from ht3.lib import run_command

import pdb


@cmd(args=1)
def debug(what):
    pdb.runcall(run_command,what)

@cmd()
def hw():
    return "Hello World"
