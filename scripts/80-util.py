from ht3.cmd import cmd

import time

@cmd()
def tea():
    """ Tea timer """
    show("sleep")
    time.sleep(1)
    show("Tee")

@cmd(args=COMMANDS)
def edit(command):
    """ Open cmd in vim """
    f, l = command.origin
    exe(EDITOR, f, '+'+str(l+1))
