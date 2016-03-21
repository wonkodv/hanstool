"""Various functions to work with Windows."""
from ht3.check import CHECK

if CHECK.os.win:
    from .message_box import *
    from .default import *
    from .hwnds import *
    from .execute import *
    from .clipboard import *
