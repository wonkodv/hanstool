"""Launch and control Neovim"""

from Env import Env, cmd, CHECK, sleep, execute_disconnected, Path, EXCEPTIONS, show
import neovim
import os.path
import inspect
import tempfile

if CHECK.os.win32:
    ADDRESS = r"\\.\pipe\nvim-pipe-{}"
    DEFAULT_NVIMGUI = ('nvim-qt', '--')
else:
    ADDRESS = "~/.config/nvim/socket-{}"
    DEFAULT_NVIMGUI = ('xterm','-e','nvim')

@cmd
def nvim(server="HT3", env={}, cwd=None):
    socket = Path(ADDRESS.format(server)).expanduser()
    if not CHECK.os.win32:
        if not socket.parent.is_dir():
            socket.parent.mkdir(parents=True)
    if not socket.exists():
        if CHECK.is_cli_frontend:
            args = Env.get('NVIM','nvim')
        else:
            args = Env.get('NVIMGUI', DEFAULT_NVIMGUI)
        if isinstance(args,str):
            args = (args,)
        args = *args, '--listen', str(socket)

        p = execute_disconnected(*args, more_env=env)

        for i in range(50):
            if socket.exists():
                break
            sleep(0.1)
        else:
            raise FileNotFoundError(f"Socket File not created by nvim. ARGS:{args} {p}")
    else:
        p = None

    nvim = neovim.attach("socket", path=str(socket))
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
