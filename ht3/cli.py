import sys
import traceback
import os
import atexit
import configparser
import os.path

from . import lib

try:
    import readline
except:
    readline = None

def setup_readline():
    if not readline:
        return False

    history = lib.Env.get('RL_HISTORY', None)
    if history:
        history = os.path.expanduser(history)
        try:
            readline.read_history_file(history)
        except FileNotFoundError:
            open(history, 'wb').close()
        hlen = readline.get_history_length()

        def save():
            newhlen = readline.get_current_history_length()
            l = newhlen - hlen
            if hasattr(readline, 'append_history_file'):
                readline.append_history_file(l, history)
            else:
                readline.write_history_file(history)
        atexit.register(save)


    def rl_complete(text, n):
        l = lib.get_completion(text)
        return l[n]
    readline.set_completer(rl_complete)
    readline.parse_and_bind('tab: complete')

def show(s, *args):
    print (str(s) % args)


def repl():
    rl = setup_readline()
    try:
        while 1:
            try:
                s = input("ht>")
                if s:
                    x = lib.run_command(s)
                    if x:
                        print(x)
            except SystemExit:
                raise
            except KeyboardInterrupt:
                return 127
            except EOFError:
                return 0
            except:
                traceback.print_exc()
    finally:
        print()
    return 0

def main(args):
    done = False
    help = False
    arg_iter = iter(args)
    lib.load_default_modules()
    lib.Env(show)

    for a in arg_iter:
        if a == '-s':
            s = next(arg_iter)
            lib.load_scripts(s)
        elif a == '-e':
            k = next(arg_iter)
            v = next(arg_iter)
            lib.Env[k]= v
        elif a == '-i':
            result = repl()
            done = True
        elif a == '-x':
            s = next(arg_iter)
            lib.run_command(s)
            done = True
        else:
            if a not in ['-h','--help','/?','/help']:
                print ("Invalid Option: "+a+""":
            Invoke:
                Allowed Arguments:
                    -s FILE         execute a script
                    -s PATH         execute a folder full of scripts. Scripts are sorted (z.10.py before a.20.py)
                    -e KEY VALUE    add a variable to the environment
                    -i              start a Read Eval Print Loop
                    -x COMMAND      execute a command
                The order of arguments is important. Nest deeply! python3 -m ht3 -x 'print(\"hello world\")' -s Script -s ScriptPath -i -s Scipt2 -i -x cleanup
                If no -i or -x is passed, you get a REPL after all args are processed.
            Environment
                All scripts and commands are exxecuted in the same environment (they all have the same globals).
                This environment is initially populated with the process'
                environment. Environment Variables that start with HT3_ are
                added twice with and without the prefix. Use the Prefix to hide
                them from other programms. Then, in order of the arguments, the
                environment is modified by -e and passed to scripts and
                commands (as globals).
                Important Environment variables (for the CLI or the default script):
                    PATH            for executing Programms
                    EDITOR          for editing Commands
                    RL_HISTORY      history of Readline completion
            """)
            return 1
    if not done:
        result = repl()
    return result

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
