import subprocess
import sys


class Env_class:
    def __init__(self):
        self.dict=dict()
    def __getattribute__(self, key):
        return self.dict[key]
    def __getitem__(self, key):
        return self.dict[key]
    def __call__(self, func):
        self.dict[func.__name__] = func
        return func
Env = Env_class()

def load_script(mod):
    exec mod in Env.dict, Env.dict


@Env
def _command_not_found_hook(s):
    try:
        c = compile(s, "<input>","exec")
        r = eval(c, Env.dict, Env.dict)
        if r != None:
            Env.show(r)
    except SyntaxError:
        shell(s)

@Env
def shell(string):
    subprocess.Popen(string, shell=True)

@Env
def exe(*args):
    return subprocess.call(args, shell=False)

@Env
def exit():
    sys.exit()
