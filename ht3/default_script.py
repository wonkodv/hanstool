"""
The default script.

Add Scripts from:
    - ht3/default_scripts/
    - ~/.config/ht3/
    - all paths from HT3_SCRIPTS environment variable
"""
from os import environ
from pathlib import Path

import pkg_resources

from ht3.check import CHECK
from ht3.scripts import add_scripts

_SCRIPT_RELOAD = False
_SCRIPT_ADD_TO_ENV = False

s = pkg_resources.resource_filename("ht3", "default_scripts")
add_scripts(s)


p = Path("~/.config/ht3").expanduser()
if p.exists():
    add_scripts(p)

s = environ.get("HT3_SCRIPTS", False)
if s:
    if CHECK.win:
        sep = ";"
    else:
        sep = ":"
    for p in s.split(sep):
        add_scripts(Path(p).expanduser())
