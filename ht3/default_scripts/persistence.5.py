import Env

import pickle
import pathlib

class Persistence:
    dict = None

    def path(self):
        return pathlib.Path(Env.get('PERSISTENCE_FILE','~/.config/ht3/persist')).expanduser()

    def load(self):
        if self.dict is not None:
            return
        try:
            with self.path().open("rb") as f:
                self.dict = pickle.load(f)
        except Exception: # forget everything on the slightest error
            self.dict = {}

    def save(self):
        assert self.dict is not None
        with self.path().open("wb") as f:
            pickle.dump(self.dict, f)

    def set(self,key,val):
        self.load()
        try:
            if self.dict[key] == val:
                return
        except KeyError:
            pass
        self.dict[key] = val
        self.save()

    __setitem__ = set

    def __getitem__(self, key):
        self.load()
        return self.dict[key]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

Per = Persistence()

Env['Per'] = Per
