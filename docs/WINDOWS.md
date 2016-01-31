
Win32 API
========

Some functions to work with windows on Windows are already imported
from `ht3.util.windows`, for example you can do

    SetForegroundWindow(FindWindow(cls='PuTTY'))

More functions can be defined the same way as in `ht3.util.windows.hwnds`.
Please submit a pull request on github if you have useful functions.


GUI Tipps
==========

You can add a folder to you task bar that is named `hanstool` by creating a
folder somewhere. Then, by right clicking on the taskbar, selecting `Add
Toolbar`, `New Toolbar` and choosing the `hanstool` folder, you get a new
toolbar.  The `GetTaskBarHandle` function looks for this toolbar.  the
`windows.10.py` file defines a `gui_do_on_start` action that places the command
window positionally over that toolbar. By calling `cmd_win_stay_on_top()`, the
command window even stays on top of the tollbar most of the time.

the DockInTaskbar function goes further and puts the command window inside the
toolbar window using `SetParent`. This looks and feels like a `DeskBand` which
are horribly difficult (activeX, Com, ...) to get working. However, if your HT
hangs, the Taskbar hangs as well. This does not happen often.

This is how it looks with a vertical Taskbar
![HT3 Gui Docked](./ht3-gui-docked.png)
