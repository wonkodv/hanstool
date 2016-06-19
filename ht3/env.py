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
        v = self.dict.get(key, default)
        if v == _DEFAULT:
            raise KeyError(key)
        return v

    __getitem__ = get

    def __getattr__(self, key, default=_DEFAULT):
        try:
            return self.get(key)
        except KeyError:
            raise AttributeError(key) from None

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
