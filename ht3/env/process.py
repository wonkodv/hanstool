import subprocess
import functools
import shlex

from . import Env
from ht3.command import register_command

@Env
def shellescape(string):
    if Check.os.posix:
        return shlex.quote(string)

    #TODO: make this safe!
    warnings.warn("UNSAFE !!! ht3.lib.shellescape")
    string = '"' + string + '"'

    return string

@Env
def shell(string, cwd=None, env=None):
    """ pass a string to a shell. The shell will parse it. """
    p = subprocess.Popen(string, shell=True, cwd=cwd, env=env)
    Env.log_subprocess(p)
    return p

@Env
def execute(*args, cwd=None, env=None):
    """ Execute a programm with arguments """
    p = subprocess.Popen(args, shell=False, cwd=cwd, env=env)
    Env.log_subprocess(p)
    return p

@Env
def execute_cmd(name, *args, **kwargs):
    register_command(functools.partial(execute, *args, **kwargs),
        name=name,
        func_name=name,
        doc='executes\n'+" ".join(shlex.quote(x) for x in args),
        origin_stacked=3)
