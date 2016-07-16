class Hook():
    def __init__(self):
        self.callbacks = []

    def register(self, cb):
        assert callable(cb)
        self.callbacks.append(cb)
        return cb

    def unregister(self, cb):
        self.callbacks.remove(cb)

    def __call__(self, *args, **kwargs):
        for c in reversed(self.callbacks):
            c(*args, **kwargs)

class NoResult(Exception):
    pass

class ResultHook(Hook):
    def __call__(self, *args, **kwargs):
        for c in reversed(self.callbacks):
            r = c(*args, **kwargs)
            if r is not None:
                return r
        raise NoResult()
