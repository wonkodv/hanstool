"""Various functions to work with Windows."""
from ht3.check import CHECK

if CHECK.os.win:
    __import__('ht3.env.windows.message_box')
    __import__('ht3.env.windows.default')
    __import__('ht3.env.windows.hwnds')
