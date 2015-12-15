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

@cmd(args=float, default=3, async=True)
def timer(t):
    """ Tea timer """
    sleep(t*60)
    MessageBox("Timer", "Done (%.1f)"%t, "TOPMOST SETFOREGROUND SYSTEMMODAL OK ICONINFORMATION")
