import traceback
from .args import Args

COMMANDS = {}

def cmd(**kwargs):
    """ @cmd() """
    def decorator(func):
        """ the actual decorator """
        tb = traceback.extract_stack()
        x = Command(func, tb, **kwargs)
        return x
    return decorator

class Command():
    def __init__(self, func, def_tb, args=None, name=None, **attrs):
        self.func=func
        self.args = Args(args)
        if name is None:
            name = func.__name__
        COMMANDS[name] = self
        self.attrs = attrs

    def __call__(self, string):
        args = self.args(string)
        return self.func(*args)
