import unittest
import time
from unittest.mock import Mock, patch

from ht3 import processwatch

def MockProcess(pid, lifetime):
    lifetime = float(lifetime)
    starttime = time.monotonic()
    def poll():
        age = time.monotonic() - starttime
        if age < lifetime:
            return None
        else:
            return 42
    p = Mock()
    p.pid = pid
    p.poll = poll
    return p

class TestProcessWatch(unittest.TestCase):
    def test_the_mock(self):
        p = MockProcess(1, 0.010)
        assert p.poll() is None
        assert p.poll() is None
        time.sleep(0.02)
        assert p.poll() == 42
        assert p.pid == 1

    def test_watch(self):
        """
        Test that processwatch.watch calls callbacks within expected time

        This Test is based on sleeping the right time and thus,
        a bit shaky. to be more accurate, multiply each time eith
        10 but then the test is slow.
        """
        with patch('ht3.processwatch.SHORT_SLEEP',0.001):

            p1 = MockProcess(1, 0.05)
            c1 = Mock()
            processwatch.watch(p1, c1)

            c1.assert_not_called()

            p2 = MockProcess(2, 0.01)
            c2 = Mock()
            processwatch.watch(p2, c2)

            c2.assert_not_called()

            time.sleep(0.02)

            c2.assert_called_once_with(p2)
            c1.assert_not_called()

            time.sleep(0.05)

            c1.assert_called_once_with(p1)
