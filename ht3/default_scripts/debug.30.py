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
    import inspect
    import os.path
    e = _LAST_ERROR
    t = e.__traceback__
    s = ""
    while(t.tb_next):
        file = t.tb_frame.f_code.co_filename
        line = t.tb_lineno
        name = t.tb_next.tb_frame.f_code.co_name
        args = inspect.formatargvalues(*inspect.getargvalues(t.tb_next.tb_frame))
        if os.path.exists(file):
            s += "{0}:{1:d}:1:{2}{3}".format(file, line, name, args)+"\n"
        t = t.tb_next

    file = t.tb_frame.f_code.co_filename
    line = t.tb_lineno
    s += "{0}:{1:d}:1:{2}: {3:s}".format(file, line, type(e).__name__, str(e.args))
    if isinstance(e, SyntaxError):
        s+= "\n{0.filename}:{0.lineno:d}:{0.offset:d}: {0.message}".format(e)
    show(s)
    import tempfile
    with tempfile.NamedTemporaryFile('wt', delete=False) as f:
        f.write(s)
        f.flush()
        vimservers = procio('vim', '--serverlist')
        vimservers = vimservers.split()
        name = "GVIM-HT3" # Names with G are put to foreground on win32
        if name in vimservers:
            execute_auto('gvim', '--servername', name,
                '--remote-send', '<C-\><C-N>:tab cfile ' + f.name+"<CR>")
        else:
            execute_auto('gvim', '--servername', name,
                '-c', ':cfile ' + f.name)

@cmd(name='import')
def _import(m:args.Option(sys.modules, allow_others=True, sort=True)):
    import importlib
    import sys
    importlib.import_module(m)
    root, _, _ = m.partition('.')
    Env[root] = sys.modules[m]
