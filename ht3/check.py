"""Provide the CHECK object to test the current environment"""
import os
import sys
import functools

__all__ = ('CHECK', )


class Group:
    def __init__(self, collection):
        self.collection = collection

    def __getattr__(self, key):
        return key in self.collection

    def __contains__(self, val):
        return val in self.collection

    def __call__(self, *vals):
        return set(vals) <= set(self.collection)

    def __repr__(self):
        return repr(self.collection)


@functools.total_ordering
class Value:
    def __init__(self, call):
        self.call = call

    def __eq__(self, other):
        return self.call() == other

    def __ne__(self, other):
        return self.call() != other

    def __gt__(self, other):
        return self.call() > other

    def __bool__(self):
        return bool(self.call())

    def __call__(self, *val):
        if len(val) == 1:
            return self.call() == val[0]
        if len(val) == 0:
            return self.call()
        raise TypeError()

    def __repr__(self):
        return repr(self.call())


class Check:
    pass


CHECK = Check()


# OS

OS = set()
OS.add(os.name)
OS.add(sys.platform)

if os.name == 'nt':
    OS.add("win")
    OS.add("windows")

CHECK.os = Group(OS)

# frontend and current_frontend are inserted by ht3.lib
