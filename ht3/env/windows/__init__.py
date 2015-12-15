"""Various functions to work with Windows."""
from ht3.check import CHECK

if CHECK.os.win:
    from . import message_box
    from . import default
    from . import hwnds
