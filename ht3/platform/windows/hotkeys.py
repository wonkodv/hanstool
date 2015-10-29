class HotkeyManager():
    def __init__(self):
        self.changes=queue.Queue()
        self.running=False
        self.hotkeys={}
        self.hotkeys_by_id={}
        self._freeid=0

    def loop(self):
        self.running=True
        while (self.running):
            try:
                while 1:
                    self.update(self.changes.get_nowait())
            except queue.Empty:
                pass
            while PeekMessage(msg, 0, 0, 0, 1):
                hk = msg.wParam
