@cmd
def list_env():
    """ List all commands """
    Env.show("\n".join(sorted(Env.dict.keys(), key=lambda k:k.lower())))

@cmd
def debug(what:CommandOrExpression):
    """ Debug a Command """
    import pdb, ht3.command, inspect
    try:
        cmd, _, args = ht3.command.get_command(what)
        pdb.set_trace()
        return cmd(args)
    except KeyError:
        x = pdb.runeval(what, Env.dict)
        return x

@cmd
def py():
    """ start a python repl """
    import sys
    return execute_auto(sys.executable)

@cmd
def debug_last_err():
    e = _LAST_ERROR
    import traceback
    tb = traceback.extract_tb(e.__traceback__)
    s = "\n".join("{0}:{1:d}:".format(*l) for l in tb)
    s += type(e).__name__
    s += str(e.args)
    if isinstance(e, SyntaxError):
        s+= "\n{0.filename}:{0.lineno:d}:{0.offset:d}:{0.message}".format(e)
    import tempfile
    with tempfile.NamedTemporaryFile('wt', delete=False) as f:
        f.write(s)
        f.flush()
        vimservers = procio('vim', '--serverlist')
        vimservers = vimservers.split()
        name = "GVIM-HT3" # Names with G are put to foreground on win32
        if name in vimservers:
            execute_auto('gvim', '--servername', name,
                '--remote-expr', ':cfile ' + f.name)
        else:
            execute_auto('gvim', '--servername', name,
                '-c', ':cfile ' + f.name)
