
if Check.frontend('ht3.cli'):
    @ht3.cli.do_on_start
    def _():
        try:
            import readline
            readline.parse_and_bind('set editing-mode vi')
        except ImportError:
            pass

@cmd
def txt():
    import os.path
    edit_file(os.path.expanduser("~/txt"),1)

@cmd(args='?', async=True)
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
