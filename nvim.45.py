"""Launch and control Neovim"""

from Env import Env, cmd, CHECK, sleep, execute_disconnected, Path, EXCEPTIONS, show
import neovim
import os.path
import inspect
import tempfile
import ht3.utils.process

if CHECK.os.win32:
    ADDRESS = r"\\.\pipe\nvim-pipe-{}"
else:
    ADDRESS = "~/.config/nvim/socket-{}"

if ht3.utils.process.which('nvim-qt'):
    DEFAULT_NVIMGUI = ('nvim-qt', '--')
else:
    DEFAULT_NVIMGUI = ('xterm','-e','nvim')

@cmd
def nvim(server="HT3", env={}, cwd=None):
    socket = Path(ADDRESS.format(server)).expanduser()
    if not socket.exists():
        if CHECK.os.posix:
            if not socket.parent.is_dir():
                socket.parent.mkdir(parents=True)
        if CHECK.is_cli_frontend:
            args = Env.get('NVIM','nvim')
        else:
            args = Env.get('NVIMGUI', DEFAULT_NVIMGUI)
        if isinstance(args,str):
            args = (args,)
        args = *args, '--listen', str(socket)

        p = execute_disconnected(*args, more_env=env, cwd=cwd)

        for i in range(50):
            if socket.exists():
                break
            sleep(0.1)
        else:
            raise FileNotFoundError(f"Socket File not created by nvim. ARGS:{args} {p}")
    else:
        if CHECK.os.posix:
            if not socket.is_socket():
                # File or dir or something
                raise OSError(f"Expected {socket} to be a socket")
        else:
            pass # windows sockets are always sockets if they exist
        show(f"Attaching to {socket}")
        p = None

    try:
        nvim = neovim.attach("socket", path=str(socket))
    except Exception as e:
        raise Exception("can not attach to socket", socket)
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
        p = inst.PROCESS
        if p:
            p.wait()
        else:
            raise NotImplementedError("Waiting on buffer in external nvim")

@cmd
def exception_trace(i:int=-1):
    """Open the traceback of the latest exception in nvim."""

    e = EXCEPTIONS[i]

    lines = []
    seen = set()

    def ff(frames, exc):
        frames = tuple(frames)
        for i, f in enumerate(frames):
            locls = f.frame.f_locals
            for name, value in sorted(locls.items()):
                try:
                    value = repr(value)
                except:
                    value = repr(type(value))+"()"
                lines.append(f'    {name} = {value}')

            file = os.path.abspath(f.filename)
            line = f.lineno

            if i:
                name = frames[i-1].function
                args = inspect.getargvalues(frames[i-1].frame)
                try:
                    args = inspect.formatargvalues(*args)
                except:
                    args = "<{} Arguments>".format(len(args))
            elif exc:
                name = type(exc).__name__
                args = str(exc.args)
            else:
                name = " ?? "
                args=""

            #if os.path.exists(file):
            lines.append(f"{file}:{line:d}: {name}{args}")

            stk = locls.get("__STACK_FRAMES__")
            if stk and id(stk) not in seen:
                seen.add(id(stk))
                lines.append("following __STACK_FRAMES__")
                ff(stk, None)
                break

    def f(e):
        t = e.__traceback__
        frames = inspect.getinnerframes(t)

        if isinstance(e, SyntaxError):
            lines.append(f"{e.filename}:{e.lineno:d}:{e.offset:d}: {e.msg}")

        if e.__cause__:
            f(e.__cause__)
            lines.append("Caused")
        if e.__context__:
            f(e.__context__)
            lines.append("Lead to")

        l = len(lines)
        ff(reversed(frames), e)
        return l

    l = f(EXCEPTIONS[i])

    s = "\n".join(lines)
    show(s)

    with tempfile.NamedTemporaryFile('wb', delete=False) as f:
        f.write(s.encode("UTF-8"))
        f.flush()
        n = nvim()
        n.command(f':cfile {f.name}')
        n.command(f':{l}cc ')
    if CHECK.is_cli_frontend:
        p = n.PROCESS
        if p:
            p.wait()
        else:
            raise NotImplementedError("Waiting on buffer in external nvim")
