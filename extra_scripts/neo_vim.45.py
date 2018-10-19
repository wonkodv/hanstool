from Env import Env, cmd, CHECK, sleep, execute_disconnected, Path, EXCEPTIONS, show
import neovim
import os.path
import inspect
import tempfile

if CHECK.os.win32:
    ADDRESS = r"\\.\pipe\nvim-pipe-{}"
else:
    ADDRESS = "~/.config/nvim/socket-{}"


@Env
@cmd
def nvim(server="HT3", env={}, cwd=None):
    server = ADDRESS.format(server)
    s = Path(server)
    more_env = { "NVIM_LISTEN_ADDRESS":server, }
    more_env.update(env)
    if not s.exists():
        if CHECK.is_cli_frontend:
            p = Env.get('NVIM',['nvim'])
        else:
            p = Env.get('NVIMGUI',['nvim-qt'])
        Env.log("starting Neovim: {} {}".format(more_env, p))
        p = execute_disconnected(*p, more_env=more_env)
    for i in range(500):
        p = None
        sleep(0.01)
        if s.exists():
            break
    nvim = neovim.attach("socket", path=server)
    nvim.PROCESS = p
    nvim.command("call rpcnotify(0, 'Gui', 'Foreground')")
    return nvim

@Env.updateable
@cmd
def edit_file(file_name:Path, line:int=0, server="HT3"):
    f = str(file_name)
    l = int(line)

    inst = nvim(server)
    inst.command("edit {}".format(file_name))
    if line:
        inst.command("normal {}gg".format(line))
    if CHECK.is_cli_frontend:
        p = isnt.PROCESS
        if p:
            p.wait()
        else:
            raise NotImplementedError("Waiting on buffer in external nvim")

@cmd
def exception_trace(i:int=-1):
    """Open the traceback of the latest exception in nvim."""

    e = EXCEPTIONS[i]
    t = e.__traceback__
    s = ""
    while(t.tb_next):
        file = t.tb_frame.f_code.co_filename
        file = os.path.abspath(file)
        line = t.tb_lineno
        name = t.tb_next.tb_frame.f_code.co_name
        args = inspect.getargvalues(t.tb_next.tb_frame)

        def  formatvalue (value):
            try:
                value = "=" + repr(value)
            except:
                value = "=<error in repr of "+repr(type(value))+">"
        args = inspect.formatargvalues(*args)

        if os.path.exists(file):
            s += "{0}:{1:d}: {2}{3}".format(file, line, name, args)+"\n"
        t = t.tb_next

    file = t.tb_frame.f_code.co_filename
    file = os.path.abspath(file)
    if os.path.exists(file):
        line = t.tb_lineno
        s += "{0}:{1:d}: {2}: {3:s}".format(file, line, type(e).__name__, str(e.args))
        if isinstance(e, SyntaxError):
            s+= "\n{0.filename}:{0.lineno:d}:{0.offset:d}: {0.msg}".format(e)
    show(s)
    with tempfile.NamedTemporaryFile('wb', delete=False) as f:
        f.write(s.encode("UTF-8"))
        f.flush()
        n = nvim()
        n.command(':cfile ' + f.name)
        n.command(':clast ')
    if CHECK.is_cli_frontend:
        p = n.PROCESS
        if p:
            p.wait()
        else:
            raise NotImplementedError("Waiting on buffer in external nvim")
