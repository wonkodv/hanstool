"""Some good Posix Commands."""

if CHECK.os.posix:
    @cmd(args=1)
    def mount(what):
        pass

    @cmd(args=1, name='o')
    def xdg_open(s):
        return execute_disconnected('xdg-open', s)
