import shlex


def Args(id):
    if not id:
        return NoArgs
    if id == 1 or id == 'all':
        return AllArgs
    if isinstance(id,str):
        if id == '?':
            return NoOrOneArgs
        if id == 'shell':
            return ShellArgs
        if id.startswith(':'):
            return GetOptsArgs(id[1:])
        if id == 'python':
            return PythonArgs
    if isinstance(id, dict):
        return DictArgs(id)

def NoArgs(string):
    string = string.strip()
    if string != '':
        raise ValueError("Not ''",string)
    return []

def NoOrOneArgs(string):
    string = string.strip()
    if string != '':
        return [string]
    return []

def AllArgs(string):
    return [string]

def ShellArgs(string):
    return shlex.split(string)

class NArgs:
    def __init__(self,n):
        self.n=n

    def __call__(self,string):
        a = shlex.split(string)
        if len(a) != self.n:
            raise ValueError ("Not %d args" % self.n, a)
        return a

class GetOptsArgs:
    def __init__(self, opts):
        self.opts = opts

    def __call__(string):
        raise NotImplemented()

class DictArgs:
    def __init__(self, dict):
        self.dict=dict

    def __call__(self, string):
        string = string.strip()
        return [self.dict[string]]
