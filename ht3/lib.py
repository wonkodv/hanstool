import configparser
import pathlib
import os.path

from .cmd import COMMANDS
from .env import Env
from . import platform

def get_command(string):
    i=0
    for c in string:
        if c == ' ':
            cmd = string[:i]
            arg = string[i+1:]
            break
        i += 1
    else:
        cmd = string
        arg = ""
    return COMMANDS[cmd], arg

def get_completion(string):
    try:
        c, args = get_command(string)
        return c.arg_parser.complete(args)
    except KeyError:
        return []

def run_command(string):
    try:
        try:
            cmd, arg = get_command(string)
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

def load_script(path):
    if path.is_dir():
        for p in path.glob('*.py'):
            load_script(p)
    elif path.is_file():
        with path.open("rt") as f:
            c = f.read()
        c = compile(c, path.as_posix(), "exec")
        exec (c, Env.dict)

def read_config(path):
    c = configparser.RawConfigParser()
    c.optionxform = lambda option: option
    c.read(path)
    if 'env' in c:
        Env.update(c['env'])
    s = c['scripts']['scripts']
    s = s.split('\n')
    for fn in s:
        fn = os.path.expandvars(fn)
        p = pathlib.Path(fn)
        load_script(p)

def load_default_modules():
    platform.load_platform_modules()
