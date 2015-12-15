"""
Watch for subprocesses that finish

In a daemon thread, repeatedly poll all registered processes. for every
one that finishes, call a callback.
Add a process with ``watch(process, callback)``
"""

import queue
import threading

PROCESS_QUEUE = queue.Queue()
SHORT_SLEEP = 0.1
LONG_SLEEP = 5.0


def watch(subprocess, callback):
    """
    Add a process to the watchlist

    Add ``subprocess`` to the list. It will be polles repeatedly
    and once it has returned, the ```callback`` function will be
    called with ``subprocess``.
    """
    PROCESS_QUEUE.put([subprocess, callback], block=False)


def _watch_thread():
    l = []
    wait = LONG_SLEEP
    def _done(p, c):
        r = p.poll()
        if r is None:
            return False
        c(p)
        return True
    while 1:
        try:
            x = PROCESS_QUEUE.get(timeout=wait)
        except queue.Empty:
            wait = min(LONG_SLEEP, 2*wait)
        else:
            wait = SHORT_SLEEP
            l.append(x)
        l = [x for x in l if not _done(*x)]


WATCH_THREAD = threading.Thread(target=_watch_thread, name='ProcessWatch', daemon=True)
WATCH_THREAD.start()
