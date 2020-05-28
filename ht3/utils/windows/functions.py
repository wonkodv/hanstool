import functools
import inspect

from ctypes import *
from ctypes.wintypes import *

kernel32 = windll.kernel32
shell32 = windll.shell32
user32 = windll.user32


def check_non_zero(r):
    return bool(r)


def check_last_err(r):
    return not GetLastError()


def check_ok(r):
    return True


notAll = set(globals().keys())


def load(dll, check=check_non_zero):
    def deco(f):
        name = f.__name__

        sig = inspect.signature(f)

        if not (
                sig.return_annotation is None
                or
                isinstance(sig.return_annotation, c_int.__mro__)
        ):
            raise TypeError(
                "return_annotation must be a ctypes datatype or None for void",
                sig.return_annotation)
        restype = sig.return_annotation

        argtypes = []
        for p in sig.parameters.values():
            if p.kind != p.POSITIONAL_OR_KEYWORD:
                raise TypeError(
                    "expected POSITIONAL_OR_KEYWORD params only", sig)
            if not isinstance(p.annotation, c_int.__mro__):
                raise TypeError(
                    "annotation must be a ctypes datatype or None for void", p)
            argtypes.append(p.annotation)

        def _errcheck(result, func, args):
            if check(result):
                return args
            e = GetLastError()
            SetLastError(0)  # clear Error Code to prevent confusion later
            s = FormatError(e)
            raise OSError(
                "ResultCheckFailed",
                check,
                result,
                e,
                s,
                func.__name__,
                args)

        func = dll[name]
        func.argtypes = argtypes
        func.restype = restype
        func.errcheck = _errcheck
        func._chek = check

        functools.update_wrapper(f, func)

        return func
    return deco


@load(kernel32, check_ok)
def GetLastError() -> DWORD: pass


@load(kernel32, check_ok)
def SetLastError(e: DWORD) -> None: pass


@load(shell32, lambda r: r > 32)
def ShellExecuteA(
        hwnd: HWND,
        lpOperation: LPCSTR,
        lpFile: LPCSTR,
        lpParameters: LPCSTR,
        lpDirectory: LPCSTR,
        nShowCmd: INT,
) -> HINSTANCE:
    pass


@load(user32, check_non_zero)
def MessageBoxW(
    hWnd: HWND,
    lpText: LPCWSTR,
    lpCaption: LPCWSTR,
    uType: UINT) -> c_int: pass


__all__ = tuple(set(globals().keys()) - notAll)
