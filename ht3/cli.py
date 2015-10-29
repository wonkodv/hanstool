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
    ok = False
    arg_iter = iter(args)
    ok = False
    arg_iter = iter(args)
    env.Env.update(os.environ)
    lib.load_default_modules()
    for a in arg_iter:
        if a == '-s':
            s = next(arg_iter)
            lib.read_config(s)
        elif a == '-i':
            interactive = True
            @env.Env
            def stop_repl():
                nonlocal interactive
                interactive = False
            while interactive:
                try:
                    ok = True
                    print ("ht> ", end='')
                    s = input()
                    if s:
                        x = lib.run_command(s)
                        if x:
                            print(x)
                except SystemExit:
                    raise
                except KeyboardInterrupt:
                    interactive = False
                except EOFError:
                    interactive = False
                except:
                    traceback.print_exc()
        elif a == '-x':
            s = next(arg_iter)
            lib.run_command(s)
            ok = True
        else:
            raise ValueError(a)


    if not ok:
        print ("Nothing to be done?\nUse arguemnt -x 'cmd' to execute command(s) or use -i to open a repl. nest deeply! ht3.cli -x setup -i -x intermediate -i -x cleanup")

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
