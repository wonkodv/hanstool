import inspect
class Hook():
    HOOKS = []
    def __init__(self, *parameters):
        self.callbacks = []
        self.parameters = parameters
        Hook.HOOKS.append(self)

    def register(self, cb):
        """Register a callback for the hook."""

        try:
            sig = inspect.signature(cb, follow_wrapped=False)
        except TypeError:
            pass # python < 3.5 or builtin or something. ignore
        else:
            try:
                sig.bind(**{p:None for p in self.parameters})
            except TypeError:
                raise TypeError("Incompatible Signature", cb, sig, self.parameters) from None
        self.callbacks.append(cb)
        return cb

    def unregister(self, cb):
        self.callbacks.remove(cb)

    def __call__(self, **kwargs):
        for c in reversed(self.callbacks):
            c(**kwargs)

class NoResult(Exception):
    pass

class ResultHook(Hook):
    def __call__(self, **kwargs):
        for c in reversed(self.callbacks):
            r = c(**kwargs)
            if r is not None:
                return r
        raise NoResult()
