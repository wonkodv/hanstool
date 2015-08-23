from .cmd import COMMANDS
from .env import Env

def get_command(string):
    i=0
    for c in string:
        if c in (' ','('):
            cmd = string[:i]
            arg = string[i:]
            break
        i += 1
    else:
        cmd = string
        arg = ""
    return COMMANDS[cmd], arg

def get_completion(string):
    try:
        c, args = get_command(string)
        return c.complete(args)
    except KeyError:
        return []

def run_command(string):
    try:
        cmd, arg = get_command(string)
        return cmd(arg)
    except KeyError:
        Env._command_not_found_hook(string)
