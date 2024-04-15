#!/usr/bin/env nix-shell
#! nix-shell -i bash
#! nix-shell -p python3Packages.xlib
#! nix-shell -p python3Packages.setuptools
#! nix-shell -p python3Packages.tkinter
#! nix-shell -p python3Packages.pynvim
#! nix-shell -p usbutils
#! nix-shell -p neovim-qt

PYTHONPATH="$(dirname -- "$(readlink -f "$0")"):$PYTHONPATH" python -m ht3 "$@"
