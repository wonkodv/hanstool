"""Functions to spawn subprocesses."""

import subprocess
import shlex
import warnings

from ht3.env import Env
from .processwatch import watch
from ht3.check import CHECK

def shellescape(string):
    if CHECK.os.posix:
        return shlex.quote(string)

    #TODO: make this safe!
    warnings.warn("UNSAFE !!! ht3.lib.shellescape")
    string = '"' + string + '"'

    return string

def shell(string, cwd=None, env=None):
    """ pass a string to a shell. The shell will parse it. """
    p = subprocess.Popen(
        string,
        shell=True,
        cwd=cwd,
        env=env,
        universal_newlines=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
    Env.log_subprocess(p)
    watch(p, lambda p: Env.log_subprocess_finished(p))
    p.shell=True
    return p

def execute(*args, cwd=None, env=None):
    """ Execute a programm with arguments """
    p = subprocess.Popen(args, shell=False, cwd=cwd, env=env)
    Env.log_subprocess(p)
    watch(p, lambda p: Env.log_subprocess_finished(p))
    p.shell=False
    return p
