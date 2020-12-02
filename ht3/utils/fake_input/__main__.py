import sys

from . import fake_input

s = " ".join(sys.argv[1:])
fake_input.fake(s)
