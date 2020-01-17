"""The ht3 main programm.

main() is called from ht3.__main__"""

import sys
import os.path
import shlex

from collections import deque
from os.path import expanduser

from . import lib
from .lib import load_frontend, run_frontends, execute_py_expression
from .command import run_command
from .env import Env
from . import scripts
from .scripts import load_scripts, add_scripts
from .check import CHECK

HELP= """The initialization and actions of the ht3 can be programmed on the commandline and/or in
the scripts.  Each argument is either a shorthand that looks like an option, or executed as a python
statement.

Initialization Shorthands (and the code they represent):
    -s SCRIPT   Add one script (not executed yet)       add_scripts(SCRIPT)
    -s FOLDER   Add all *.py files in FOLDER            add_script(FOLDER)
    -l          Sort and Load all added scripts         load_scripts()
    -f FRONTEND Load a frontend (don't start it yet)    load_frontend(FRONTEND)
    -e KEY VAL  Define Static (survives reload)         put_static(KEY, VAL)
    -d          add ht3/default_script.py and load all scripts

Action Shorthands:
    -r          Run all loaded Frontends                run_frontends()
    -c COMMAND  Run a command                           run_command(COMMAD)
    -x CODE     Execute code

Before an Action Shorthand, all added scripts are loaded. After an Action shorthand, no default
actions are performed, unless an initialization command follows.
After Initialization, the following default actions are executed:
    1. ht3/default_script.py is added if no scripts were added
    2. all added but not loaded scripts are loaded
    3. if no frontend was added, ht3.cli is added
    4. frontends are run
"""


class ArgumentError(ValueError):
    pass

def load_default_script():
    if not scripts.SCRIPTS:
        if not scripts.ADDED_SCRIPTS:
            import pkg_resources
            s = pkg_resources.resource_filename('ht3','default_script.py')
            add_scripts(s)
    while scripts.ADDED_SCRIPTS:
        load_scripts()

def put_env(k, v):
    try:
        v = int(v)
    except ValueError:
        pass
    Env.put_static(k,v)

POSSIBLE_ARGUMENTS = [
    #   short    Long              Function          ParamNo Done/Action
    [  '-s',  '--add-script',      add_scripts,          1,  False  ],
    [  '-l',  '--load-scripts',    load_scripts,         0,  False  ],
    [  '-f',  '--load-frontend',   load_frontend,        1,  False  ],
    [  '-r',  '--run-frontends',   run_frontends,        0,  True   ],
    [  '-d',  '--default-script',  load_default_script,  0,  False  ],
    [  '-e',  '--set-env',         put_env,       2,  False  ],
    [  '-c',  '--command',         run_command,          1,  True   ],
    [  '-x',  '--execute',         "code",               1,  True   ],
]

def parse(args):
    arg_iter = iter(args)
    for a in arg_iter:
        if a.startswith('-'):
            for short, long, function, params, done in POSSIBLE_ARGUMENTS:
                if a == short or a == long:
                    if params:
                        try:
                            p = tuple(next(arg_iter) for _ in range(params))
                        except StopIteration:
                            raise ArgumentError(f"Expecting a parameter", a)
                    else:
                        p = ()
                    yield function, p, done
                    break
            else:
                raise ArgumentError(f"Invalid option {a}")
        else:
            yield 'code', (a,), False

def precompile(args):
    for i, (f, p, d) in enumerate(args):
        if f == 'code':
            c, = p
            c = compile(c, f"<command line {i}>", "exec")
            p = (c,)
        yield f, p, d

def main(args):
    args = precompile(parse(args))
    try:
        args = list(args) # consume to get errors early
    except ArgumentError as e:
        print (*e.args)
        print (HELP)
        return 1

    try:
        # populate "globals" so that Env can act as "locals" and not have those functions in it
        glob = {}
        for f in [add_scripts, load_scripts, load_frontend, run_command, run_frontends, Env.put_static]:
            glob[f.__name__] = f
        done = False
        for f, a, done in args:
            if done:
                load_default_script()
            if f == 'code':
                code, = a
                exec(code, glob, Env.persistent_dict)
                Env._reload()
            else:
                f(*a)
        if not done:
            load_default_script()
            if not lib.FRONTEND_MODULES:
                load_frontend('ht3.cli')
            run_frontends()
    except Exception:
        if Env.get('DEBUG',False):
            import traceback
            traceback.print_exc()
            import pdb
            pdb.post_mortem()
        raise
