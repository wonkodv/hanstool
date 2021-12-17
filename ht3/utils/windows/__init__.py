"""Various functions to work with Windows."""
from ht3.check import CHECK

if CHECK.os.win:
    from .clipboard import *
    from .default import *
    from .functions import *
    from .hwnds import *
    from .message_box import *
    from .process import *
