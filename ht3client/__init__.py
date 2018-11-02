"""Client to ht3.daemon.

Send one command via commandline or open a repl

execute with "--help" for usage info.
"""
import pickle
import os
import socket
import pathlib
import sys
import io
import argparse
import traceback

ARG_PARSER = argparse.ArgumentParser(description="Client for ht3.daemon")
ARG_PARSER.add_argument("-u", "--socket",    help="Path to the UNIX Socket ht3.daemon listens on")
ARG_PARSER.add_argument("-s", "--server",    help="Path to the UNIX Socket ht3.daemon listens on")
ARG_PARSER.add_argument("-p", "--port",      help="Port on Server that ht3.daemon listens to")
ARG_PARSER.add_argument("-4", "--ipv4",      help="Use IPv4 instead of IPv6")
ARG_PARSER.add_argument("-c", "--complete", action='store_true',    help="Complete the (partial) command instead of executing")
ARG_PARSER.add_argument("-q", "--quiet", action='store_true',       help="Hide Exception Traceback")
ARG_PARSER.add_argument("command", nargs="?",                       help="Command to Send (start a repl if none given)")


class RemoteException(Exception):
    pass

# Some Code is redundant with ht3.daemon

class HT3Client():
    def __init__(self, typ, adr):
        self.sock = socket.socket(typ, socket.SOCK_STREAM)
        self._adr = adr

    def connect(self):
        self.sock.connect(self._adr)
        self.sock_file = self.sock.makefile("rwb")

    def disconnect(self):
        self.sock_file.close()
        self.sock.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self,*_):
        self.disconnect()

    def _send(self, command, arg):
        pickle.dump([command, arg], self.sock_file)
        self.sock_file.flush()
        while True:
            try:
                obj = pickle.load(self.sock_file)
                s, t, r = obj
                if s == "OK":
                    yield t,r
                elif s == "EXCEPTION":
                    raise RemoteException(t)
                else:
                    raise TypeError(s, t, r)
            except EOFError:
                return

    def complete(self, s):
        for t, r in self._send("COMPLETE", s):
            if t == "COMPLETION":
                yield r
            elif t == "COMPLETION-DONE":
                return
            else:
                raise TypeError(t,r)

    def command(self, s):
        t, r = next(self._send("COMMAND", s))
        if t in ("RESULT", "REPR", "EXIT"):
            return r
        raise TypeError(s,t,r)

    def ping(self):
        t, r = next(self._send("PING"))
        if t == "PONG":
            return
        raise TypeError(s,t,r)

def repl(*socket_info):
    with HT3Client(*socket_info) as htc:
        try:
            import readline
        except ImportError:
            pass
        else:
            completion_cache=[]
            def rl_complete(text, n):
                if n == 0:
                    completion_cache.clear()
                    try:
                        comp = htc.complete(text)
                    except Exception as e:
                        print(e)
                        return
                    completion_cache.extend(comp)
                if n < len(completion_cache):
                    s = completion_cache[n]
                    return s
            readline.set_completer(rl_complete)
            readline.set_completer_delims('') # complete with the whole line
            readline.parse_and_bind('tab: complete')

        try:
            while True:
                try:
                    s = input("HT3: ")
                    if s:
                        r = htc.command(s)
                        print(repr(r))
                except RemoteException as e:
                    print(e.args[0])
                except KeyboardInterrupt:
                    print()
        except EOFError:
            print()

def main(options):
    adr = ('::1', 4267)
    typ = socket.AF_INET6

    if options.socket:
        if options.port or options.server or options.ipv4:
            raise TypeError("Specify either socket or server/port")
        adr = os.path.expanduser(options.socket)
        typ = socket.AF_UNIX
    elif options.server:
        if options.port:
            adr = (options.server, options.port)
        else:
            adr = (options.server, 4267)
        if options.ipv4:
            typ = socket.AF_INET
    else:
        if hasattr(socket,'AF_UNIX'):
            p = pathlib.Path('~/.config/ht3/socket').expanduser()
            if p.exists():
                adr = str(p)
                typ = socket.AF_UNIX

    try:
        if options.complete:
            with HT3Client(typ, adr) as htc:
                r = htc.complete(options.command)
                for l in r:
                    print (l)
        elif options.command:
            with HT3Client(typ, adr) as htc:
                r = htc.command(options.command)
            if r is not None:
                print(r)
        else:
            repl(typ, adr)
    except RemoteException as e:
        print(e.args[0], file=sys.stderr)
    except Exception as e:
        if options.quiet:
            print(e, file=sys.stderr)
        else:
            traceback.print_exc()
        return 1
