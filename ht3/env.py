class Env_class:
    """ Class to record all variables and functions of
    all scripts and command invocations in one namespace """

    def __init__(self):
        self.dict=dict()

    def __getattr__(self, key):
        return self.dict[key]

    def __getitem__(self, key):
        return self.dict[key]

    def __setitem__(self, key, val):
        self.dict[key] = val

    def __call__(self, func):
        """ decorator to put functions in Env """
        self.dict[func.__name__] = func
        return func

    def update(self, dict, overwrite=False):
        if overwrite:
            self.dict.update(dict)
        else:
            for k in dict:
                if not k in self.dict:
                    self[k] = dict[k]

Env = Env_class()
