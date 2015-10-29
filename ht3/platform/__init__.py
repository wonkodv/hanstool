import sys
import os

def _load(s):
    try:
        __import__(__package__+'.'+s)
    except ImportError:
        import warnings
        warnings.warn('could not load plattform module: %s' % s)

def load_platform_modules():
    if os.name == 'nt':
        _load('windows')
    if os.name == 'java':
        _load('java')
    if os.name == 'posix':
        _load('posix')
        if sys.platform.startswith('linux'):
            _load('linux')
