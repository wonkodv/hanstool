import Env

import os
from pathlib import Path

# Get OS Variables

for k, v in os.environ.items():
    if k[:4] == "HT3_":
        Env[k[4:]] = v

PATH = Env["PATH"] = [Path(p) for p in os.get_exec_path()]
