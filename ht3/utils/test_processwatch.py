import time
import unittest
from threading import Event
from unittest.mock import Mock, patch

from ht3.utils import processwatch


class TestProcessWatch(unittest.TestCase):
    @patch("ht3.utils.processwatch.SHORT_SLEEP", 0.001)
    @patch("ht3.utils.processwatch.LONG_SLEEP", 0.001)
    def test_watch(self):
        """ Test processwatch.watch calls callbacks once after poll is not None."""
        event = Event()
        sentinel = Mock()
        sentinel.poll = lambda: (event.set(), None)[1]
        processwatch.watch(sentinel, None)

        def wait():
            """Wait till all were polled >=1 time."""
            event.clear()
            event.wait()
            event.clear()
            event.wait()

        p1 = Mock()
        p1.poll.return_value = None
        c1 = Mock()

        p2 = Mock()
        p2.poll.return_value = None
        c2 = Mock()

        processwatch.watch(p1, c1)

        wait()
        assert not c1.called

        processwatch.watch(p2, c2)

        wait()
        assert not c1.called
        assert not c2.called

        p2.poll.return_value = 42

        wait()
        assert not c1.called
        c2.assert_called_once_with(p2)
        c2.reset_mock()

        p1.poll.return_value = 0
        wait()

        c1.assert_called_once_with(p1)
        c1.reset_mock()

        wait()
        wait()
        assert not c1.called
        assert not c2.called
