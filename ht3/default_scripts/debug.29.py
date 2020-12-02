import dis
import importlib
import inspect
import io
import os.path
import pdb
import sys
import tempfile
import traceback

import ht3.command
from Env import *


@cmd
def debug(string: args.Union(args.Command, args.Python)):
    """ Debug a Command """

    p = pdb.Pdb()
    cmd = get_command(string)
    p.rcLines.append("b cmd.run")
    p.rcLines.append("c")
    p.set_trace()
    cmd()


@cmd
def disassemble(s: args.Python):
    o = evaluate_py_expression(s.lstrip())
    b = io.StringIO()
    dis.dis(o, file=b)
    show(b.getvalue())


@cmd
def py():
    """ start a python repl """
    execute_auto(sys.executable)


EXCEPTIONS = Env["EXCEPTIONS"] = []


@EXCEPTION_HOOK.register
@COMMAND_EXCEPTION_HOOK.register
def add_exception(exception, command=None):
    EXCEPTIONS.append(exception)


@cmd(name="import")
def _import(m: args.Option(sys.modules, allow_others=True, sort=True)):
    """Import a module into Env."""
    root = m.partition(".")[0]
    importlib.import_module(m)
    Env[root] = sys.modules[root]


@cmd
def update_check():
    """Check for updates in git."""
    p = str(Path(__file__).parent)
    procio("git", "-C", p, "fetch")
    status = procio("git", "-C", p, "status", "-sb")
    if "[" in status:
        status = status.partition("[")[2].partition("]")[0]
        show("Git status: " + status)
    else:
        show("Git up to date")


def version():
    try:
        p = Path(ht3.__file__).parent.parent
        v = procio(f"git -C {p} describe --tags")
        return v.strip()
    except BaseException:
        return "version unknown (depends on git describe)"


@cmd(name="version")
def _version():
    v = version()
    show(v)


print("HansTool {} on Python {}".format(version(), sys.version))


@cmd
def threadlist():
    show("\n".join("{0.ident: 10d} {0.name}".format(t) for t in threading.enumerate()))


@cmd
def processlist():
    import psutil

    show(
        "\n".join(
            "{: 10d} {}".format(p.pid, p.name())
            for p in psutil.Process().children(recursive=True)
        )
    )


if Env.get("MAKELEVEL", False):

    @EXCEPTION_HOOK.register
    def _format_exceptions_liek_make(exception):
        t = exception.__traceback__
        while t.tb_next:
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
            file, line, type(exception).__name__, str(exception.args)
        )
        if isinstance(exception, SyntaxError):
            s += "\n{0.filename}:{0.lineno:d}:{0.offset:d}: {0.msg}".format(exception)
        print(s)


@cmd
def raise_exception():
    """Raise an exception with a nice and complicated Traceback / Cause list."""

    def a(x):
        b(x + 1)

    def b(y):
        raise Exception("arg1", "arg2", "arg3", y)

    try:
        a(10)
    except Exception as e:
        try:
            a(20)
        except Exception as e2:
            try:
                raise e2 from e
            except BaseException:
                raise ValueError(42)


@DEBUG_HOOK.register
def trace_log(message):
    if Env.get("TRACE_LOG", False):
        print()
        traceback.print_stack()
        print("Debug Message")
        print(message)


@ALERT_HOOK.register
def trace_alert(message):
    if Env.get("TRACE_ALERT", False):
        print()
        traceback.print_stack()
        print("Alert Message")
        print(message)
