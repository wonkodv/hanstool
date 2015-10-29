import pathlib
import os.path

from .cmd import COMMANDS, cmd
from .env import Env
from . import platform

def parse_command(string):
    i=0
    for c in string:
        if c in [' ','\t']:
            cmd = string[:i]
            arg = string[i:]
            break
        i += 1
    else:
        cmd = string
        arg = ""
    return cmd, arg

def run_command(string):
    try:
        try:
            cmd, arg = parse_command(string)
            cmd = COMMANDS[cmd]
            res = cmd(arg)
            Env['_'] = res
            return res
        except KeyError:
            res = Env._command_not_found_hook(string)
            Env['_'] = res
            return res
    except Exception as e:
        Env['_'] = e
        raise e

def load_scripts(path):
    if not isinstance(path, pathlib.Path):
        path = str(path)
        path = os.path.expanduser(path)
        path = pathlib.Path(path)
    if path.is_dir():
        l = path.glob('*.py')
        l = sorted(l, key=lambda p: [int(p.suffixes[-2][1:]),p] if len(p.suffixes)>1 else ["",p] )
        for p in l:
            load_scripts(p)
    elif path.is_file():
        with path.open("rt") as f:
            c = f.read()
        c = compile(c, path.as_posix(), "exec")
        exec (c, Env.dict)
    else:
        raise Exception("neither file nor dir in load_Scripts", path)


def load_default_modules():
    Env(load_scripts)
    Env(run_command)
    Env(parse_command)
    Env(cmd)
    Env['COMMANDS'] = COMMANDS
    platform.load_platform_modules()
