import os
import sys


class Group:
    def __init__(self, col):
        self.col = col

    def __getattr__(self, key):
        return key in self.col

    def __contains__(self, val):
        return val in self.col

    def __call__(self, *vals):
        for v in vals:
            if not v in self.col:
                return False
        return True

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
