import os

if os.name == 'nt':

    from ctypes import windll
    from ht3.cmd import cmd

    @cmd(name='o', args=1)
    def shellexecute(s):
        windll.shell32.ShellExecuteW(0, "open", s, None, "", 1)


    @cmd(args=COMMANDS, name="#")
    def explore_command(cmd):
        """ Show the directory or file used in the target commands source in explorer"""
        for c in cmd.__wrapped__.__code__.consts:
            if isinstance(str, c):
                try:
                    p = Path(c)
                    if p.exists():
                        if not p.is_dir():
                            p = p.parent
                        execute("explorer","/select"+str(p))
                except:
                    pass

