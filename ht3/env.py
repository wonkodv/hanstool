"""The `Env` object, access point to the unified namespace."""

_DEFAULT = object()

class _Env_class:
    """ Class to record all variables and functions of
    all scripts and command invocations in one namespace """

    def __init__(self):
        object.__setattr__(self, 'dict', dict())
        object.__setattr__(self, 'persistent_dict', dict())

    def _reload(self):
        object.__setattr__(self, 'dict', dict())
        self.dict.update(self.persistent_dict)

    def put_persistent(self, k, v):
        """Put values into the dict that survives reload."""
        self.persistent_dict[k] = v
        self.dict[k] = v

    def put(self, key, val):
        self.dict[key] = val

    __setitem__ = put

    def __setattr__(self, key, val):
        raise AttributeError("Dont set Attributes on Env")

    def get(self, key, default=_DEFAULT):
        return self.dict.get(key, default)

    def __getitem__(self, key):
        return self.dict[key]

    __getattr__ = __getitem__

    def __iter__(self):
        return iter(self.dict)

    def __call__(self, func):
        """ decorator to put functions in Env """
        self.dict[func.__name__] = func
        return func

    def __str__(self):
        return "Env: " + ", ".join(self.dict)

    def __repr__(self):
        return str(self.dict)

Env = _Env_class()
