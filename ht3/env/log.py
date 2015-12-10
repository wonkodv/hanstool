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
    print(traceback.format_exc())

@Env
def log(s):
    if Env.get('DEBUG', False):
        print(s)

@Env
def log_subprocess(p):
    if Env.get('DEBUG', False):
        print("spawned process: %d, %r" % (p.pid, p.args))

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
