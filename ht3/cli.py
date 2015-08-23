import sys
import traceback
import os

from . import env
from . import lib

print ("HT CLI")

@env.Env
def show(s, *args):
    print (str(s) % args)

def main(args):
    interactive = False
    ok = False
    arg_iter = iter(args)
    env.Env.update(os.environ)
    for a in arg_iter:
        if a == '-s':
            s = next(arg_iter)
            lib.read_config(s)
        elif a == '-i':
            interactive = True
        elif a == '-x':
            s = next(arg_iter)
            lib.run_command(s)
            ok = True

    while 1:
        try:
            print ("ht> ", end='')
            s = input()
            if s:
                x = lib.run_command(s)
                if x:
                    print(x)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            return 0
        except:
            traceback.print_exc()


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
