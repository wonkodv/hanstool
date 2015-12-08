import sys
import pathlib

from . import lib
from .command import run_command
from .env import Env
from .env import initial


DEFAULT_SCRIPTS_TEXT='''Using the default scripts. You should copy them to ~/.config/ht3
and modify them:
    sh$ mkdir -p ~/.config/ht3/
    sh$ cp "%s/*" ~/.config/ht3/
    sh$ touch ~/.config/tools.50.py
    sh$ ht
    ht> l
    ht> e
    ht> ++ tools newComand
If you already have script(s), use them with -s.  '''
HELP= """call ht with the following arguments:
    -s SCRIPT   Load a script
    -s FOLDER   Load several scripts
    -f FRONTEND Load a frontend (dont start it yet)
    -e VAR VAL  Set a Variable to a string value
    -x COMMAND  execute a command
    -r          Run all loaded Frontends """

def main(args):
    try:
        _x = False
        _f = False
        _r = False
        _s = False
        arg_iter = iter(args)

        for a in arg_iter:
            if a == '-s':
                s = next(arg_iter)
                lib.load_scripts(s)
                _s = True
            elif a == '-e':
                k = next(arg_iter)
                v = next(arg_iter)
                Env[k]= v
            elif a == '-f':
                f = next(arg_iter)
                lib.load_frontend(f)
                _f = True
            elif a == '-r':
                lib.run_frontends()
                _r = True
            elif a == '-x':
                s = next(arg_iter)
                run_command(s)
                _x = True
            else:
                if a not in ['-h','--help','/?','/help']:
                    print ("Invalid Option: "+a)
                print (HELP)

                return 1
        if not _s:
            p = pathlib.Path('~/.config/ht3')
            if p.is_dir():
                lib.load_scripts(p)
            else:
                import pkg_resources
                s = pkg_resources.resource_filename(__name__,'default_scripts')
                print(DEFAULT_SCRIPTS_TEXT % s)
                lib.load_scripts(s)
        if (not _r and _f):
            lib.run_frontends()
        elif (not _f and not _x):
            print("Loading default frontend `ht3.cli` Load others with `-f`")
            lib.load_frontend('ht3.cli')
            lib.run_frontends()
        return 0
    except:
        if Env.get('DEBUG',False):
            import pdb
            pdb.post_mortem()
        raise

sys.exit(main(sys.argv[1:]))
