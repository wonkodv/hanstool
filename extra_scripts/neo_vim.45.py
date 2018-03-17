from Env import Env, cmd, CHECK, sleep, execute_disconnected, Path, EXCEPTIONS, show
import neovim
import os.path
import inspect
import tempfile

NVIM_PATH = r"c:\users\riegel\tools\Neovim\bin\nvim-qt.exe"

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
        Env.log("starting Neovim: {} {}".format(more_env, NVIM_PATH))
        p = execute_disconnected(NVIM_PATH, more_env=more_env)
    for i in range(500):
        sleep(0.01)
        if s.exists():
            break
    return neovim.attach("socket", path=server)

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
        nvim().command(':cfile ' + f.name)
