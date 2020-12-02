"""Implement process-related functions that behave special on windows."""

import ctypes
import os
import pathlib
import shlex
import subprocess

from ht3.complete import filter_completions_i
from ht3.env import Env
from ht3.utils import process


def execute(exe, *args, is_split=..., shell=False, **kwargs):
    """Find an executable in PATH, optionally appending PATHEXT extensions, then execute."""

    if not shell:
        if is_split is ...:
            is_split = len(args) > 0

        if is_split:
            # replace exe with looked up exe
            # execute("c:/program files/mozilla/firefox.exe", "http://example.com")
            p = which(exe)
            if not p:
                raise FileNotFoundError("Cannot find executable", exe)
            exe = str(p)
        else:
            if args:
                raise ValueError("Expecting only 1 string if not `is_split`")

            # replace 1st word in exe with looked up 1st word

            # TODO: windows does not do this exactly
            e = shlex.split(exe)[0]
            if e == exe:
                # execute("ls")
                p = which(e)
                if p:
                    # TODO: shellescape is not exactly the right thing on windows ?
                    exe = shellescape(str(p))
                else:
                    pass  # good luck with that
            elif exe.startswith(e + " "):
                # execute("ls -l")
                # try to change the 1st word to the full path of an executable
                # file
                tail = exe[len(e) :]
                p = which(e)
                if p:
                    e = shellescape(str(p))
                else:
                    pass  # good luck with that

                assert tail[0] == " "
                exe = e + tail
            else:
                pass
                # execute('"c:/program files/mozilla/firefox.exe" http://example.com')
                # execute('"c:/program files/mozilla/firefox.exe"')

                # execute("c:/program files/mozilla/firefox.exe")
                #     MSDN: The System tries to interpret the possibilities in the following order:
                #       c:\program.exe files\sub dir\program name
                #       c:\program files\sub.exe dir\program name
                #       c:\program files\sub dir\program.exe name
                #       c:\program files\sub dir\program name.exe

    # Ugly flag stuff so windows does not create ConsoleWindows for processes
    # which have the io streams set.
    if all(
        x in kwargs and kwargs[x] == subprocess.PIPE
        for x in ("stdin", "stdout", "stderr")
    ):
        if "startupinfo" not in kwargs:
            si = subprocess.STARTUPINFO()
            si.dwFlags = subprocess.STARTF_USESHOWWINDOW
            si.wShowWindow = subprocess.SW_HIDE
            kwargs["startupinfo"] = si

    # TODO: handle messed up encoding of windows shell processes

    return process.execute(exe, *args, is_split=is_split, shell=shell, **kwargs)


_extensions = os.environ.get("PATHEXT", "").split(os.pathsep)
_paths = [pathlib.Path(p) for p in os.get_exec_path()]


def which(exe):
    try:
        return next(_get_exe_path(exe, True, False))
    except StopIteration:
        return None


def _get_exe_path_ext(p, full_path, glob):
    if glob:
        glob = "*"
    else:
        glob = ""
    if p.suffix:
        for c in p.parent.glob(p.name + glob):
            if full_path:
                yield str(c)
            else:
                yield str(c), ""
    else:
        for ext in _extensions:
            for c in p.parent.glob(p.name + glob + ext):
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
        for c in Env.get("PATH", _paths):
            f = c / s
            yield from _get_exe_path_ext(f, full_path, glob)


def complete_executable(s):
    """Find all possible executables in PATH, optionally appending PATHEXT.

    If there is more than file with the same name, only differing in the
    extension, yield both, else yield only the name"""
    s = shlex.split(s)
    if len(s) != 1:
        return ()
    s = s[0]

    values = {}
    for exe, ext in _get_exe_path(s, False, True):
        short = exe[: -len(ext)]
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
    r = int(r)
    if r == 0:
        return True
    if r == 0x102:  # WAIT_TIMEOUT
        raise TimeoutError()
    if r == 0x80:  # WAIT_ABANDONED
        raise ChildProcessError("Wait abandoned", r)
    if r == -1:  # WAIT_FAILED
        return False
    try:
        raise ctypes.WinError()
    except BaseException:
        raise ValueError("Unexpected return value", r)
