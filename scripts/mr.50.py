import os.path
import readline
import time

readline.parse_and_bind('set editing-mode vi')

@cmd
def txt():
    execute(EDITOR,os.path.expanduser("~/txt"))

@cmd(args='?')
def tea(t=3):
    """ Tea timer """
    t = t*60
    show("sleep "+str(t))
    time.sleep(t)
    show("Tee")

