from Env import *

import faulthandler
import ht3.command
import importlib
import inspect
import os.path
import pdb
import sys
import tempfile

@cmd
def debug(string:args.Union(args.Command, args.Python)):
    """ Debug a Command """

    p = pdb.Pdb()
    cmd = get_command(string)
    p.rcLines.append("b self.run")
    p.rcLines.append("c")
    p.runcall(cmd)

@cmd
def py():
    """ start a python repl """
    return execute_auto(sys.executable)

EXCEPTIONS = Env['EXCEPTIONS'] = []

@EXCEPTION_HOOK.register
@COMMAND_EXCEPTION_HOOK.register
def add_exception(exception, command=None):
    EXCEPTIONS.append(exception)

@cmd
def exception_trace(i:int=-1):
    """Open the traceback of the latest exception in gvim with :cload."""

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
    with tempfile.NamedTemporaryFile('wb', delete=False) as f:
        f.write(s.encode("UTF-8"))
        f.flush()
        vimservers = procio('vim', '--serverlist')
        vimservers = vimservers.split()
        name = "GVIM-HT3" # Names with G are put to foreground on win32
        if name in vimservers:
            execute_auto('gvim', '--servername', name,
                    '--remote-send', r'<C-\><C-N>:tab cfile ' + f.name+"<CR>:clast<CR>")
        else:
            execute_auto('gvim', '--servername', name,
                '-c', ':cfile ' + f.name)

@cmd(name='import')
def _import(m:args.Option(sys.modules, allow_others=True, sort=True)):
    """Import a module into Env."""
    root = m.partition('.')[0]
    importlib.import_module(m)
    Env[root] = sys.modules[root]

@cmd
def update_check():
    """Check for updates in git."""
    p = str(Path(__file__).parent)
    procio('git','-C',p,'fetch')
    status = procio('git','-C',p,'status','-sb')
    if '[' in status:
        status = status.partition('[')[2].partition(']')[0]
        show("Git status: "+status)
    else:
        show("Git up to date")

@cmd
def threadlist():
    show("\n".join("{0.ident: 10d} {0.name:>10s}".format(t) for t in threading.enumerate()))

if Env.get('MAKELEVEL',False):
    @EXCEPTION_HOOK.register
    def _format_exceptions_liek_make(exception):
        t = exception.__traceback__
        while(t.tb_next):
            file = t.tb_frame.f_code.co_filename
            file = os.path.abspath(file)
            line = t.tb_lineno
            name = t.tb_next.tb_frame.f_code.co_name
            args = inspect.formatargvalues(*inspect.getargvalues(t.tb_next.tb_frame))
            if os.path.exists(file):
                print("{0}:{1:d}:1:{2}{3}".format(file, line, name, args))
            t = t.tb_next

        file = t.tb_frame.f_code.co_filename
        file = os.path.abspath(file)
        line = t.tb_lineno
        s = "{0}:{1:d}:1:{2}: {3:s}".format(
                file,
                line,
                type(exception).__name__,
                str(exception.args)
            )
        if isinstance(exception, SyntaxError):
            s += "\n{0.filename}:{0.lineno:d}:{0.offset:d}: {0.msg}".format(exception)
        print(s)

if Env.get('DEBUG', False):
    warnings.simplefilter("error")
