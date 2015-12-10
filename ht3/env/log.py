import traceback
from . import Env

@Env
def show(s):
    print(s)

@Env
def log_command(cmd):
    if Env.get('DEBUG', False):
        print("command: " + cmd)

@Env
def log_command_finished(result):
    if result is None:
        if not Env.get('DEBUG', False):
            return
    print("Result: " + repr(result))

@Env
def log_error(e):
    t = type(e)
    tb = e.__traceback__
    for s in traceback.format_exception(t, e, tb):
        print(s)

@Env
def log(s):
    if Env.get('DEBUG', False):
        print(s)

@Env
def log_subprocess(p):
    if Env.get('DEBUG', False):
        print("spawned process: %d, %r" % (p.pid, p.args))

@Env
def log_subprocess_finished(p):
    if p.returncode > 0 or Env.get('DEBUG', False):
        print("process finished: %d with %d" % (p.pid, p.returncode))

@Env
def log_thread(t):
    if Env.get('DEBUG', False):
        print("spawned thread: %d, %r" % (t.pid, t.target))

@Env
def log_thread_finished(r):
    if result is None:
        if not Env.get('DEBUG', False):
            return
    print("ThreadResult: " + repr(result))
