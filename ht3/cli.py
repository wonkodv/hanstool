import sys
import traceback
import os
import atexit
import configparser
import os.path

from . import lib
from .lib import Env

try:
    import readline
except:
    readline = None

def main(args):
    done = False
    help = False
    arg_iter = iter(args)

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

def repl():
    setup_readline()
    try:
        while 1:
            try:
                s = input(Env.CLI_PROMPT())
            except KeyboardInterrupt:
                return 127
            except EOFError:
                return 0
            else:
                if s:
                    try:
                        x = lib.run_command(s)
                    except KeyboardInterrupt:
                        print("\n!!Aborted")
                    except SystemExit:
                        raise
                    except:
                        traceback.print_exc()
                    else:
                        if x:
                            print(x)
    finally:
        print()
    return 0

def setup_readline():
    if not readline:
        return False

    history = Env.get('RL_HISTORY', None)
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

    completion_cache=[]

    def rl_complete(text, n):
        nonlocal completion_cache
        if n == 0:
            try:
                completion_cache = list(lib.get_completion(text))
            except:
                traceback.print_exc()
            #print("\nCompletion of %s, cache: %s\n--> %s" % (text, completion_cache, text),end='')
        return completion_cache[n]
    readline.set_completer(rl_complete)
    readline.set_completer_delims('')
    readline.parse_and_bind('tab: complete')


@Env
def CLI_PROMPT():
    return "ht3> "

# API

@Env
def show(s, *args, **kwargs):
    print (str(s) % args)

@Env
def log(s, *args, **kwargs):
    print (str(s) % args)

@Env
def edit_file(path, line):
    execute(EDITOR, f)

Env['help'] = help

Env['INTERFACE'] = "ht3.cli"


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
