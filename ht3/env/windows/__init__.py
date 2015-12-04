
from ht3.lib import Check

if Check.os.win:
    from . import message_box
    from . import default
    from . import hwnds
