"""The ht3 main programm.

main() is called from ht3.__main__"""

import sys
import os.path

from . import lib
from .command import run_command
from .env import Env
from .scripts import load_scripts, add_scripts


HELP= """call ht with the following arguments:
    -s SCRIPT   Add a script
    -s FOLDER   Add several scripts
    -l          Load all added unloaded scripts or default scripts
    -f FRONTEND Load a frontend (dont start it yet)
    -r          Run all loaded Frontends
    -e VAR VAL  Set a Variable to a string value in Env
    -x COMMAND  execute a command
    -c CODE     execute python code in Env
"""

def main(args):
    """Run the Hans Tool."""
    try:
        _x = False
        _f = False
        _r = False
        _l = False
        _s = False
        arg_iter = iter(args)

        def add_default_scripts():
            s = Env.get('HT3_SCRIPTS', False)
            if s:
                for p in s.split(':'): #TODO use ; on Win
                    add_scripts(os.path.expanduser(p))
            else:
                import pkg_resources
                s = pkg_resources.resource_filename(__name__,'default_scripts')
                add_scripts(s)
                s = os.path.expanduser('~/.config/ht3')
                if os.path.exists(s):
                    add_scripts(s)

        for a in arg_iter:
            if a == '-s':
                s = next(arg_iter)
                s = os.path.expanduser(s)
                add_scripts(s)
                _s = True
                _l = False
            elif a == '-l':
                if not _s:
                    add_default_scripts()
                load_scripts()
                _l = True
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
            elif a == '-e':
                k = next(arg_iter)
                v = next(arg_iter)
                Env.put_persistent(k, v)
            elif a == '-c':
                c = next(arg_iter)
                lib.execute_py_expression(c)
            else:
                if a not in ['-h','--help','/?','/help']:
                    print ("Invalid Option: "+a)
                print (HELP)
                return 1
        if not _l:
            if not _s:
                add_default_scripts()
            load_scripts()

        if not (_f or _x):
            lib.load_frontend('ht3.cli')
            _f = True

        if not _r and _f:
            lib.run_frontends()
        return 0
    except Exception:
        if Env.get('DEBUG',False):
            import traceback
            traceback.print_exc()
            import pdb
            pdb.post_mortem()
        raise

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
