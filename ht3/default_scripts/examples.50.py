"""Soome example commands and configuration."""

if CHECK.frontend('ht3.cli'):
    @cli_do_on_start
    def _():
        try:
            import readline
            readline.parse_and_bind('set editing-mode vi')
        except ImportError:
            pass

@cmd
def txt():
    edit_file(expanduser("~/txt"))

@cmd(async=True)
def timer(t:float=3, event:str="Done"):
    """ timer timer """
    sleep(t*60)
    option_dialog("Timer", "Timer up ({0})".format(event),"OK")


def _complete_virtualbox(s=None):
    """Helper function for the vb command, get the names of installed boxes."""
    import subprocess
    p = subprocess.Popen(
        ["vboxmanage", "list", "vms"],
        universal_newlines=True,
        stdout=subprocess.PIPE)
    output, _ = p.communicate()
    for s in sorted(output.split('\n')):
        x = s.split()
        if x:
            yield x[0][1:-1]

@cmd
def vb(box:_complete_virtualbox=None):
    """Open VirtualBox (the manager) or start a box with the approximate name."""
    if not box:
        execute_disconnected("virtualbox")
    else:
        execute_disconnected("vboxmanage", "startvm", box)

@cmd
def history_stats(n:int=10):
    with open(GUI_HISTORY) as f:
        show(
            sorted((b,a) for a,b in
                collections.Counter(
                    ht3.command.parse_command(s.strip())[0] for s in f
                ).items()
            )[-n:]
        )
