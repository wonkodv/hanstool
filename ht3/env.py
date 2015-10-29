class Env_class:
    """ Class to record all variables and functions of
    all scripts and command invocations in one namespace """

    def __init__(self):
        self.dict=dict(Env=self)

    def __getattr__(self, key):
        return self.dict[key]

    def __getitem__(self, key):
        return self.dict[key]

    def __setitem__(self, key, val):
        self.dict[key] = val

    def get(self, key, default=None):
        return self.dict.get(key, default)

    def __iter__(self):
        return iter(self.dict)

    def __call__(self, func):
        """ decorator to put functions in Env """
        self.dict[func.__name__] = func
        return func
