#!/usr/bin/env python3
"""Python Wrapper for the Trace32 C Remote API

http://www2.lauterbach.com/pdf/api_remote.pdf
"""

from pathlib import Path
import sys
from ctypes import CFUNCTYPE, POINTER, byref, c_char, c_char_p, c_int, c_ulonglong, c_voidp, cdll, sizeof
import itertools

class T32Error(Exception):
    pass

try:
    import Env

    @Env.cmd
    def t32cmd(cmd:str):
        with Connection() as c:
            c.do(cmd)
except ImportError:
    Env = None
    # Not HT3

class T32API():
    def __init__(self):
        lib = None
        if Env:
            try:
                p = Env['T32_LIB']
                lib  = cdll.LoadLibrary(str(p))
            except KeyError:
                pass
        if sizeof(c_voidp)==4:    # 32 Bit
            libs = ("t32api.dll", "t32api.so",)
        else:
            libs = ("t32api64.dll", "t32api64.so", )
        for d, n in itertools.product( ("", Path(__file__).parent, r"C:\T32\demo\api\capi\dll"), libs):
                p = str(Path(d) / n)
                try:
                    lib  = cdll.LoadLibrary(p)
                    break
                except OSError as e:
                    pass
        if lib is None:
            raise FileNotFoundError("No T32api lib found")

        self.lib = lib

        self.Config = CFUNCTYPE(c_int, c_char_p, c_char_p)(lib.T32_Config)
        self.Config.errcheck = self._errcheck
        self.Init   = CFUNCTYPE(c_int)(lib.T32_Init)
        self.Init.errcheck = self._errcheck
        self.Attach   = CFUNCTYPE(c_int, c_int)(lib.T32_Attach)
        self.Attach.errcheck = self._errcheck
        self.Ping   = CFUNCTYPE(c_int)(lib.T32_Ping)
        self.Ping.errcheck = self._errcheck
        self.Cmd   = CFUNCTYPE(c_int, c_char_p)(lib.T32_Cmd)
        self.Cmd.errcheck = self._errcheck
        self.GetMessage   = CFUNCTYPE(c_int, c_char_p, POINTER(c_ulonglong))(lib.T32_GetMessage)
        self.GetMessage.errcheck = self._errcheck
        self.Exit   = CFUNCTYPE(c_int)(lib.T32_Exit)
        self.Exit.errcheck = self._errcheck

    def _errcheck(self, result, func, args):
        if result != 0:
            raise T32Error("Error in T32API: %d" %(result, ), func, args, result)

    @classmethod
    def instance(cls):
        i = cls()
        cls.instance = lambda:i
        return i

class Connection:

    def __init__(self, host='localhost', port=20000, packetlen=1024):
        self.host = host
        self.port = port
        self.packetlen = packetlen
        self.api = T32API.instance()

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, *args):
        self.close()
        return False


    def init(self):
        self.api.Config(b"NODE=", self.host.encode("ASCII"))
        self.api.Config(b"PORT=", str(self.port).encode("ASCII"))
        self.api.Config(b"PACKLEN=", str(self.packetlen).encode("ASCII"))
        self.api.Init()
        self.api.Attach(1)

    def do(self, cmd):
        self.api.Cmd(cmd.encode("ASCII"))

    def get_message(self):
        raise NotImplementedError("Buggy")
        buf = (c_char * 300)()
        status = c_ulonglong(0)
        self.api.GetMessage(buf, byref(status))
        v = status.value
        if v:
            typ = [m for i,m in self._message_codes.items() if v&i]
            msg = str(buf.value.decode("latin-1"))
            return typ, msg

    def ping(self):
        self.api.Ping()

    def close(self):
        self.api.Exit()

if __name__ == '__main__':
    with Connection() as c:
        for s in sys.argv[1:]:
            print ("Running command: "+s)
            c.do(s)
