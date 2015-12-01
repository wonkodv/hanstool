import sys

from . import lib
from .command import run_command
from .env import Env
from .env import initial

HELP= """ look in the README.md under _COMMAND LINE_ or _Environment_ for help !  """

def main(args):
    try:
        _x = False
        _f = False
        _r = False
        arg_iter = iter(args)

        for a in arg_iter:
            if a == '-s':
                s = next(arg_iter)
                lib.load_scripts(s)
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
        if (not _r and _f):
            lib.run_frontends()
        elif (not _f and not _x):
            lib.load_frontend('ht3.cli')
            lib.run_frontends()
        return 0
    except:
        if Env.get('DEBUG',False):
            import pdb
            pdb.post_mortem()
        raise

sys.exit(main(sys.argv[1:]))
