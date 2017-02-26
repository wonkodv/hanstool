"""Soome example commands and configuration."""

from Env import *

import random
import subprocess
import string


if CHECK.frontend('ht3.cli'):
    import ht3.cli
    @ht3.cli.do_on_start
    def import_readline():
        try:
            import readline
            readline.parse_and_bind('set editing-mode vi')
        except ImportError:
            pass

@cmd
def txt():
    """Edit ~/txt."""
    edit_file(expanduser("~/txt"))

@cmd(threaded=True)
def timer(t:float, event:str="Done"):
    """ timer timer """
    sleep(t*60)
    option_dialog("Timer", "Timer up ({0})".format(event),"OK")

def complete_virtualbox(s=None):
    """Helper function for the vb command, get the names of installed boxes."""
    vms = procio("vboxmanage list vms", shell=False, is_split=False)

    # "debian" {fbc948a5-7b8b-489c-88b0-7f5eaceb150e}
    for s in sorted(vms.split('\n')):
        if s:
            x = s.split('"')
            yield x[1]

@cmd
def vb(box:complete_virtualbox=None):
    """Open VirtualBox (the manager) or start a box with the approximate name."""
    if not box:
        execute_disconnected("virtualbox")
    else:
        execute_disconnected("vboxmanage", "startvm", box)

@cmd
def rand(low:int=0, high:int=0xFFFFFFFF):
    """Copy a random number to the Clipboard."""
    r = random.randint(low,high)
    set_clipboard("0x{:8X}".format(r))
    show(r)

@cmd
def password():
    set_clipboard("".join(random.sample(string.printable, 12)))
