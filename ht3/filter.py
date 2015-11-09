import os
import sys


class Value:
    def __init__ (self, col, key):
        self.col = col
        self.key = key

    def __bool__(self):
        return self.key in self.col

    def __int__(self):
        return int(self.col[key])

class Group:
    def __init__(self, col):
        self.col = col

    def __getattr__(self, key):
        return Value(self.col, key)

    def __contains__(self, val):
        return val in self.col

class Filter_class():
    OS = set()
    FRONTENDS = set()
    os = Group(OS)
    frontend = Group(FRONTENDS)




Filter = Filter_class()

Filter.OS.add(os.name)
Filter.OS.add(sys.platform)

if os.name == 'nt':
    Filter.OS.add("win")
    Filter.OS.add("windows")

__all__ = ['Filter']
