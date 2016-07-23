import ht3.env

ht3.env.Env['TEST_VAL'] = 42

from Env import *

assert TEST_VAL == 42

