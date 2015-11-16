from ht3.lib import Check

if Check.os.windows:
    from . import windows
