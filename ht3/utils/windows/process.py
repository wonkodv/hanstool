"""Implement process-related functions that behave special on windows."""

import pathlib
import subprocess
import os
import shlex
import ctypes
from ht3.utils import process
from ht3.env import Env
from ht3.complete import filter_completions_i

def execute(exe, *args, is_split=..., shell=False, **kwargs):
    """Find an executable in PATH, optionally appending PATHEXT extensions, then execute."""
    if not isinstance(exe,str):
        raise TypeError("Expecting a string as exe", exe, type(exe))
    for a in args:
        if not isinstance(a, str):
            raise TypeError("Expecting only strings as args", a, type(a))
    if not shell:
        if is_split is ...:
            if len(args) == 0:
                # works: execute("ls -l")
                # doesn't work: execute("c:/program files/mozilla/firefox.exe")
                # works: execute('"c:/program files/mozilla/firefox.exe"')
                # works: execute('"c:/program files/mozilla/firefox.exe" http://example.com')
                # works: execute("c:/program files/mozilla/firefox.exe", "http://example.com")
                is_split = False
            else:
                is_split = True

        if is_split:
            # replace exe with looked up exe
            p = which(exe)
            if not p:
                raise FileNotFoundError("Cannot find executable",exe)
            exe = str(p)
        else:
            # replace 1st word in exe with looked up 1st word
            if args:
                raise ValueError("Expecting only 1 string if not `is_split`")
            e = shlex.split(exe)[0]
            if exe.startswith(e+" "):
                # try to change the 1st word to the full path of an executable file
                tail = exe[len(e):]
                p = which(e)

                if p:
                    e = shellescape(str(p))
                else:
                    pass # good luck with that, maybe its a shell command

                assert tail[0] == ' '
                exe = e + tail


    # Ugly flag stuff so windows does not create ConsoleWindows for processes which have the io streams set.
    if all(x in kwargs and kwargs[x] == subprocess.PIPE for x in ('stdin','stdout','stderr')):
        if not 'startupinfo' in kwargs:
            si = subprocess.STARTUPINFO()
            si.dwFlags = subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
            kwargs['startupinfo'] = si

    # TODO: handle messed up encoding of windows shell processes

    return process.execute(exe, *args, is_split=is_split, shell=shell, **kwargs)

_extensions = os.environ.get('PATHEXT','').split(os.pathsep)
_paths = [pathlib.Path(p) for p in os.get_exec_path()]

def which(exe):
    try:
        return next(_get_exe_path(exe, True, False))
    except StopIteration:
        return None

def _get_exe_path_ext(p, full_path, glob):
    if glob:
        glob = '*'
    else:
        glob = ''
    if p.suffix:
        for c in p.parent.glob(p.name+glob):
            if full_path:
                yield str(c)
            else:
                yield str(c), ''
    else:
        for ext in _extensions:
            for c in p.parent.glob(p.name+glob+ext):
                if full_path:
                    yield str(c)
                else:
                    yield c.name, ext

def _get_exe_path(s, full_path, glob):
    p = pathlib.Path(s)
    parts = p.parts
    if len(parts) > 1:
        yield from _get_exe_path_ext(p, full_path, glob)
    else:
        for c in Env.get('PATH',_paths):
            f = c / s
            yield from _get_exe_path_ext(f, full_path, glob)

def complete_executable(s):
    """Find all possible executables in PATH, optionally appending PATHEXT.

    If there is more than file with the same name, only differing in the 
    extension, yield both, else yield only the name"""
    s = shlex.split(s)
    if len(s) != 1:
        return
    s = s[0]

    values = {}
    for exe, ext in _get_exe_path(s, False, True):
        short = exe[:-len(ext)]
        if short in values:
            values[short].add(exe)
        else:
            values[short] = {exe}

    def gen():
        for short, longs in sorted(values.items()):
            if len(longs) == 1:
                yield short
            else:
                yield from longs
    return filter_completions_i(s, gen())


def shellescape(*strings):
    return subprocess.list2cmdline(strings)


def WaitForInputIdle(process, timeout=-1):
    r = ctypes.windll.user32.WaitForInputIdle(process._handle, timeout)
    if r == 0:
        return True
    if r == 0x102:
        return False
    raise ctypes.WinError()
