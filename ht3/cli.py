
from . import env
from . import lib

from .env import Env

print ("HT CLI")

@Env
def show(s, *args):
    print (str(s) % args)


f = open('ht3/eo.py')

env.load_script(f)


while 1:
    s = raw_input()
    lib.run_command(s)
