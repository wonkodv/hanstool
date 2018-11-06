#!/usr/bin/env python3
"""Python Wrapper for the Trace32 C Remote API

http://www2.lauterbach.com/pdf/api_remote.pdf
"""

from pathlib import Path
import sys
from ctypes import CFUNCTYPE, POINTER, byref, c_char, c_char_p, c_int, c_ulonglong, c_voidp, cdll, sizeof

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

def lib_path():
    if Env:
        try:
            return Env['T32_LIB']
        except KeyError:
            pass
    if sizeof(c_voidp)==4:    # 32 Bit
        libs = ("t32api.dll", "t32api.so",)
    else:
        libs = ("t32api64.dll", "t32api64.so", )
    for lib in libs:
        for d in ("", Path(__file__).parent, r"C:\T32\demo\api\capi\dll"):
            f = Path(d) / lib
            if f.exists():
                return f
    raise FileNotFoundError("No T32api lib found")

class Connection:
    p = lib_path()
    t32api  = cdll.LoadLibrary(str(p))

    def _errcheck(result, func, args):
        if result != 0:
            raise T32Error("Error in T32API: %d" %(result, ), func, args, result)
    T32_Config = CFUNCTYPE(c_int, c_char_p, c_char_p)(t32api.T32_Config)
    T32_Config.errcheck = _errcheck
    T32_Init   = CFUNCTYPE(c_int)(t32api.T32_Init)
    T32_Init.errcheck = _errcheck
    T32_Attach   = CFUNCTYPE(c_int, c_int)(t32api.T32_Attach)
    T32_Attach.errcheck = _errcheck
    T32_Ping   = CFUNCTYPE(c_int)(t32api.T32_Ping)
    T32_Ping.errcheck = _errcheck
    T32_Cmd   = CFUNCTYPE(c_int, c_char_p)(t32api.T32_Cmd)
    T32_Cmd.errcheck = _errcheck
    T32_GetMessage   = CFUNCTYPE(c_int, c_char_p, POINTER(c_ulonglong))(t32api.T32_GetMessage)
    T32_GetMessage.errcheck = _errcheck
    T32_Exit   = CFUNCTYPE(c_int)(t32api.T32_Exit)
    T32_Exit.errcheck = _errcheck

    def __init__(self, host='localhost', port=20000, packetlen=1024):
        self.host = host
        self.port = port
        self.packetlen = packetlen

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, *args):
        self.close()
        return False


    def init(self):
        self.T32_Config(b"NODE=", self.host.encode("ASCII"))
        self.T32_Config(b"PORT=", str(self.port).encode("ASCII"))
        self.T32_Config(b"PACKLEN=", str(self.packetlen).encode("ASCII"))
        self.T32_Init()
        self.T32_Attach(1)

    def do(self, cmd):
        self.T32_Cmd(cmd.encode("ASCII"))

    def get_message(self):
        raise NotImplementedError("Buggy")
        buf = (c_char * 300)()
        status = c_ulonglong(0)
        self.T32_GetMessage(buf, byref(status))
        v = status.value
        if v:
            typ = [m for i,m in self._message_codes.items() if v&i]
            msg = str(buf.value.decode("latin-1"))
            return typ, msg

    def ping(self):
        self.T32_Ping()

    def close(self):
        self.T32_Exit()

if __name__ == '__main__':
    with Connection() as c:
        for s in sys.argv[1:]:
            print ("Running command: "+s)
            c.do(s)
