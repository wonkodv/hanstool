import readline
readline.parse_and_bind('set editing-mode vi')


@cmd
def txt():
    import os.path
    execute(EDITOR,os.path.expanduser("~/txt"))

@cmd(args='?')
def tea(t=3):
    """ Tea timer """
    import time
    if t:
        t = int(t)
    else:
        t = 3
    t = t*60
    time.sleep(t)
    show("Tee")
