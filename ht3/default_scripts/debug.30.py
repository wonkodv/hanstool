from Env import *

import ht3.command
import importlib
import inspect
import inspect
import os.path
import pdb
import sys
import sys
import tempfile

@cmd
def list_env():
    """ List all commands """
    Env.show("\n".join(sorted(Env.dict.keys(), key=lambda k:k.lower())))

@cmd
def debug(what:args.Union(args.Command, args.Python)):
    """ Debug a Command """
    pdb.runcall(ht3.command.run_command, what)

@cmd
def py():
    """ start a python repl """
    return execute_auto(sys.executable)


EXCEPTIONS = []

@EXCEPTION_HOOK.register
@COMMAND_EXCEPTION_HOOK.register
def add_exception(exception, **kwargs):
    EXCEPTIONS.append(exception)

@cmd
def debug_err(i:int=-1):
    e = EXCEPTIONS[i]
    t = e.__traceback__
    s = ""
    while(t.tb_next):
        file = t.tb_frame.f_code.co_filename
        file = os.path.abspath(file)
        line = t.tb_lineno
        name = t.tb_next.tb_frame.f_code.co_name
        args = inspect.formatargvalues(*inspect.getargvalues(t.tb_next.tb_frame))
        if os.path.exists(file):
            s += "{0}:{1:d}:1:{2}{3}".format(file, line, name, args)+"\n"
        t = t.tb_next

    file = t.tb_frame.f_code.co_filename
    file = os.path.abspath(file)
    line = t.tb_lineno
    s += "{0}:{1:d}:1:{2}: {3:s}".format(file, line, type(e).__name__, str(e.args))
    if isinstance(e, SyntaxError):
        s+= "\n{0.filename}:{0.lineno:d}:{0.offset:d}: {0.msg}".format(e)
    show(s)
    with tempfile.NamedTemporaryFile('wt', delete=False) as f:
        f.write(s)
        f.flush()
        vimservers = procio('vim', '--serverlist')
        vimservers = vimservers.split()
        name = "GVIM-HT3" # Names with G are put to foreground on win32
        if name in vimservers:
            execute_auto('gvim', '--servername', name,
                '--remote-send', '<C-\><C-N>:tab cfile ' + f.name+"<CR>")
        else:
            execute_auto('gvim', '--servername', name,
                '-c', ':cfile ' + f.name)

@cmd(name='import')
def _import(m:args.Option(sys.modules, allow_others=True, sort=True)):
    root = m.partition('.')[0]
    importlib.import_module(m)
    Env[root] = sys.modules[root]


@cmd
def update_check():
    p = str(Path(__file__).parent)
    procio('git','-C',p,'fetch')
    status = procio('git','-C',p,'status','-sb')
    if '[' in status:
        status = status.partition('[')[2].partition(']')[0]
        show("Git status: "+status)
    else:
        show("Git up to date")
