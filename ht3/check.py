class Group:
    def __init__(self, collection):
        self.collection = collection

    def __getattr__(self, key):
        return key in self.collection

    def __contains__(self, val):
        return val in self.collection

    def __call__(self, *vals):
        return set(vals) <= set(self.collection)

class Value:
    def __init__(self, call):
        self.call = call

    def __eq__(self, other):
        return self.call() == other

    def __ne__(self, other):
        return self.call() != other

    def __call__(self, *val):
        if len(val) == 1:
            return self.call() == val[0]
        if len(val) == 0:
            return self.call()
        raise TypeError()

class Check:
    pass
