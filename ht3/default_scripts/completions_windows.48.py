from pathlib import Path

from Env import CHECK, EXECUTABLE_W_ARGS_COMPLETE_HOOK, exe_completer

if CHECK.os.win:

    @exe_completer("control")
    def complete_control(parts):
        """Completions for the Control Panel"""
        for p in [
            r"C:\Windows\System32",
            r"C:\Windows\SysWOW64",
            r"C:\Windows\Sysnative",
        ]:
            for c in Path(p).glob("*.cpl"):
                yield c.name

        return True
