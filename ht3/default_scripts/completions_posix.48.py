import shlex

from Env import CHECK, Path, exe_completer, procio, which


@exe_completer("ls")
def _complete_ls(parts):
    if parts[-1] == "-":
        for f in "lrst10":
            yield "-" + f
        return True


@exe_completer("killall")
def _complete_killall(parts):
    if len(parts) == 2:
        s = procio("ps xo command=")
        for p in s.split("\n"):
            p = p.strip()
            if p:
                p = shlex.split(p)
                p = Path(p[0])
                yield p.name
        return True
