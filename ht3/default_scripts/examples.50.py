"""Soome example commands and configuration."""

if CHECK.frontend('ht3.cli'):
    @ht3.cli.do_on_start
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
def timer(t:float=3):
    """ Tea timer """
    sleep(t*60)
    MessageBox("Timer", "Done (%.1f)"%t, "TOPMOST SETFOREGROUND SYSTEMMODAL OK ICONINFORMATION")


def _vb_get_vms(s=None):
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

@cmd(args=1,complete=_vb_get_vms)
def vb(box=None):
    """Open VirtualBox (the manager) or start a box with the approximate name."""
    if not box:
        execute("virtualbox")
    else:
        import difflib
        boxes = _vb_get_vms()
        box = difflib.get_close_matches(box, boxes, 1, 0.1)[0]
        execute("vboxmanage", "startvm", box)
