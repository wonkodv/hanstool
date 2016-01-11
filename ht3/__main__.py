"""The ht3 main programm."""
import sys
import os.path

from . import lib
from .command import run_command
from .env import Env
from .scripts import load_scripts


HELP= """call ht with the following arguments:
    -s SCRIPT   Load a script
    -s FOLDER   Load several scripts
    -f FRONTEND Load a frontend (dont start it yet)
    -e VAR VAL  Set a Variable to a string value
    -x COMMAND  execute a command
    -r          Run all loaded Frontends """

def main(args):
    """Run the Hans Tool."""
    try:
        _x = False
        _f = False
        _r = False
        _s = False
        arg_iter = iter(args)

        for a in arg_iter:
            if a == '-s':
                s = next(arg_iter)
                s = os.path.expanduser(s)
                load_scripts(s)
                _s = True
            elif a == '-e':
                k = next(arg_iter)
                v = next(arg_iter)
                Env.put_persistent(k, v)
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

        if not (_f or _x):
            print("Loading default frontend `ht3.cli` Load others with `-f`")
            lib.load_frontend('ht3.cli')
            _f = True

        if not _s:
            s = Env.get('SCRIPTS', False)
            if s:
                for p in s.split(':'): #TODO use ; on Win
                    load_scripts(os.path.expanduser(p))
            else:
                import pkg_resources
                s = pkg_resources.resource_filename(__name__,'default_scripts')
                load_scripts(s)
                s = os.path.expanduser('~/.config/ht3')
                if os.path.exists(s):
                    load_scripts(s)
        if not _r and _f:
            lib.run_frontends()
        return 0
    except:
        if Env.get('DEBUG',False):
            import traceback
            traceback.print_exc()
            import pdb
            pdb.post_mortem()
        raise

sys.exit(main(sys.argv[1:]))
