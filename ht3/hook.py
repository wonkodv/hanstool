import inspect


class Hook:
    """Delegate calls to all registered callbacks in reversed order.

    If at least one handler returns True, the Hook returns True ("handled")"""

    HOOKS = []

    def __init__(self, *parameters):
        """Create a hook which is with the passed **kwargs."""
        self.callbacks = []
        self.parameters = parameters
        Hook.HOOKS.append(self)

    def register(self, cb):
        """Register a callback for the hook.

        A basic signature check is performed to ensure the callback can
        be called with the hook's **kwargs."""

        try:
            sig = inspect.signature(cb, follow_wrapped=False)
        except TypeError:
            pass  # python < 3.5 or builtin or something. ignore
        else:
            try:
                sig.bind(**{p: None for p in self.parameters})
            except TypeError:
                raise TypeError(
                    "Incompatible Signature", cb, sig, self.parameters
                ) from None
        self.callbacks.append(cb)
        return cb

    def unregister(self, cb):
        self.callbacks.remove(cb)

    def __call__(self, **kwargs):
        handled = False
        for c in reversed(self.callbacks):
            r = c(**kwargs)
            if r:
                handled = True
        return handled

    def __repr__(self):
        return f"{self.__class__.__name__}({self.callbacks})"


class NoResult(Exception):
    pass


class ResultHook(Hook):
    """Invokes the registered callbacks until one doesn't return `None`"""

    def __call__(self, **kwargs):
        for c in reversed(self.callbacks):
            r = c(**kwargs)
            if r is not None:
                return r
        raise NoResult()


class GeneratorHook(Hook):
    """Yields elements of registered callbacks.

    When iterating over the result of a called registered function raises
    a StopIteration with a value that is true-ish, no other callbacks
    are called. This is NOT achived by returning a list or tuple
    as Generator:
        def foo():
            yield 1
            yield 2
            return True

    as Iterator
        class Iter:
            def __next__(self):
                if self.exausted():
                    raise StopIteration(True)
    """

    def __call__(self, **kwargs):
        for c in reversed(self.callbacks):
            i = iter(c(**kwargs))
            try:
                while True:
                    yield next(i)
            except StopIteration as e:
                if e.value:
                    return e.value
