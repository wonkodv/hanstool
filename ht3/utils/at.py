"""
Do things at specific times

In a daemon thread, wait until it is time to do a job
"""

import queue
import threading


class IntervalSchedule:
    """ Schedule after every elapsed timedelta."""

    def __init__(self, td):
        self.td = td

    def next(self, last):
        return last + self.td


class CronScheduler:
    def __init__(self, h, m, s):
        self.h = h
        self.m = m
        self.s = s

    def next(self, last):
        def m(a, b):
            if a[0] == "*":
                return b
            if a[0] == "/":
                mod = int(a[1:])
                r = b % mod
                if r:
                    b = b + mod - r
                return b
            if a[0] == "=":
                return ()
            raise ValueError("??", a[0])


class Job:
    def __init__(self, cb, schedule):
        self.cb = cb
        self.schedule = schedule
        self.last = self.datetime.datetime.now()

    def trigger(self):
        now = self.datetime.datetime.now()
        if self.next() <= now:
            self.cb()
        self.last = now

    def next(self):
        return self.schedule.next(self.last)


_EVENT = threading.Event()
jobs = tuple()


def register(job=None, *, callback=None, schedule=None):
    global jobs
    if job is None:
        if schedule is None:
            raise ValueError("schedule is None")
        if callback is None:
            raise ValueError("callback is None")
        job = Job(callback, schedule)
    jobs = jobs + (job,)
    _EVENT.set()


def _watch_thread():
    wait = 10000
    while True:
        if not _EVENT.wait(timeout=wait):
            continue


WATCH_THREAD = threading.Thread(target=_watch_thread, name="ProcessWatch", daemon=True)
WATCH_THREAD.start()
