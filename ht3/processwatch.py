import queue
import threading

PROCESS_QUEUE = queue.Queue()
SHORT_SLEEP = 0.1
LONG_SLEEP = 5


def watch(p, callback):
    PROCESS_QUEUE.put([p, callback], block=False)

def watch_thread():
 #   import pdb; pdb.set_trace()
    l = []
    wait = LONG_SLEEP
    def done(p, c):
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
        l = [ x for x in l if not done(*x)]


WATCH_THREAD = threading.Thread(target=watch_thread, name='ProcessWatch', daemon=True)
WATCH_THREAD.start()
