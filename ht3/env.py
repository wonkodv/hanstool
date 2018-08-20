"""The `Env` object, access point to the unified namespace."""

_DEFAULT = object()

import types
import sys
import inspect
import functools
import collections.abc

class _Env_class(types.ModuleType, collections.abc.Mapping):
    """Common Env to be used by scripts

    import Env
    from Env.mainscript import *
    """

    def __init__(self):
        object.__setattr__(self, '_finalized', False)

        self.dict = dict()
        self.persistent_dict = dict()
        self.__package__ = "Env"
        self.__name__ = "Env"
        self.__path__ = []
        self.__file__ = __file__
        super().__init__("Env", _Env_class.__doc__) # init as Module
        self._finalized = True # stop attribute setting

        for k in 'file','path','name','package':
            k = '__{}__'.format(k)
            self.put_persistent(k, getattr(self,k))

    @property
    def __all__(self):
        return tuple(k for k in self.dict if k[0] != '_')

    def _reload(self):
        self.dict.clear()
        self.dict.update(self.persistent_dict)

    def put_persistent(self, key, val):
        """Put values into the dict that survives reload."""
        self.persistent_dict[key] = val
        self.dict[key] = val

    def put(self, key, val):
        self.dict[key] = val

    __setitem__ = put

    def __setattr__(self, key, val):
        if not getattr(self,'_finalized'):
            self.__dict__[key] = val
        elif inspect.ismodule(val):
            self.put(key, val) # importing a script as sub module of Env
        else:
            raise AttributeError("Dont set Attributes on Env")

    def get(self, key, default=_DEFAULT):
        v = self.dict.get(key, default)
        if v == _DEFAULT:
            raise KeyError(key)
        return v

    def __getitem__(self, key):
        return self.dict[key]

    def __getattr__(self, key):
        try:
            return self.dict[key]
        except KeyError:
            raise AttributeError(key) from None

    def update(self, *args):
        self.dict.update(*args)

    def items(self):
        return self.dict.items()

    def __len__(self):
        return len(self.dict)

    def __iter__(self):
        return iter(self.dict)

    def __call__(self, func):
        """Decorator to put functions in Env
        """
        self.put(func.__name__, func)
        return func

    def updateable(self, func):
        """Put an updateable wrapper of a function in Env

            @Env
            def a(): return 1
            x = Env.a
            @Env
            def a(): return 2

            assert a() == 2
            assert a != x
            assert x() == 2
        """
        name = func.__name__
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            w = self.get(name)
            f = inspect.unwrap(w)
            return f(*args, **kwargs)
        self.put(name, wrapper)
        return wrapper


    def __str__(self):
        return "Env: " + ", ".join(self.dict)

    def __repr__(self):
        return str(self.dict)


Env = _Env_class()

sys.modules['Env'] = Env
