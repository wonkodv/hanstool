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
    if isinstance(id, dict):
        return DictArgs(id)

def NoArgs(string):
    """ Takes no arguments """
    string = string.strip()
    if string != '':
        raise ValueError("Not expecting an argument!, got: "+repr(string))
    return []

def NoOrOneArgs(string):
    """ Takes no or one argument of arbitrary format """
    string = string.strip()
    if string != '':
        return [string]
    return []

def AllArgs(string):
    """ Takes one argument of arbitrary format """
    return [string]

def ShellArgs(string):
    """ Takes multiple shellencoded arguments  """
    return shlex.split(string)

class NArgs:
    """ Takes %d shellencoded arguments """
    def __init__(self,n):
        self.n=n
        self.__doc__ = self.__doc__ % n

    def __call__(self,string):
        a = shlex.split(string)
        if len(a) != self.n:
            raise ValueError ("Not %d args" % self.n, a)
        return a

class GetOptsArgs:
    """ Takes the following "getopt" arguments:\n%s """
    def __init__(self, opts):
        self.opts = opts
        self.__doc__ = self.__doc__ % (opts,)

    def __call__(string):
        raise NotImplemented()

class DictArgs:
    """ Takes one of these argumwents: \n%s """
    def __init__(self, dict):
        self.dict=dict
        self.__doc__ = self.__doc__ % (", ".join(dict),)

    def __call__(self, string):
        string = string.strip()
        return [self.dict[string]]
