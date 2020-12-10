import hotkey

from . import command


def get_hotkey(hk):
    return hotkey.get_hotkey(hk)


def get_all_hotkeys():
    return tuple(hotkey.HOTKEYS.values())


def free_all_hotkeys():
    for hk in get_all_hotkeys():
        try:
            hk.free()
        except hotkey.Error:
            pass


def reload_command_hotkey(c):
    hk = c.attrs["HotKey"]

    try:
        c._HotKey.free()
    except AttributeError:
        pass

    def run_command():
        c(hk, "")()

    run_command.__qualname__ = c.__qualname__
    hko = hotkey.HotKey(hk, run_command)
    c.attrs["_HotKey"] = hko


def reload_hotkeys():
    """For all commands that have a HotKey attribute, register a hotkey.

    If the command already had a hotkey, it is freed first
    """

    for c in command.COMMANDS.values():
        if "HotKey" in c.attrs:
            reload_command_hotkey(c)


@command.COMMAND_EXCEPTION_HOOK.register
def _command_exception(exception, command):
    if command.frontend == "ht3.hotkey":
        return True  # Don't raise the exception


def start():
    pass


def loop():
    reload_hotkeys()
    hotkey.run()


def stop():
    hotkey.stop(wait=False)
