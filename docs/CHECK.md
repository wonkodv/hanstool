Check where you are
==================


With `ht3.check.CHECK` you can test:

*   Which plattform you are on
*   Whether a frontend is loaded
*   Which frontend is currently running

assuming you import CHECK into your Env.

Plattform
---------

In a script or inside a function or command, you can use
`if CHECK.os.win:` to test if you are on windows. Other attributes:

*   all values possible by sys.plattform (`win32`, `cygwin`, `freebsd`,
    `linux`, `darwin`, ...)
*   all values possible by os.name (`posix`, `java`, `nt`, ...)
*   `win` and `windows` are added if `os.name == 'nt'`

There are several ways to test for these:

*   `CHECK.os.posix`
*   `CHECK.os('posix')`
*   `'posix' in CHECK.os`


Loaded Frontends
----------------

In the same way as for os, you can check which frontends are installed:

*   `CHECK.frontend('ht3.hotkey')`
*   `CHECK.frontend('ht3.hotkey', 'ht3.gui')` to check that both are loaded
*   `'ht3.htd' in CHECK.frontend`


Current Frontend
----------------

This one does not work at script run time, only inside commands or
functions called by commands.

*   `CHECK.current_frontend('ht3.cli')`
*   `CHECK.current_frontend == 'ht3.cli'`
*   `CHECK.current_frontend() == 'ht3.cli'`


Python Version
--------------

*   `CHECK.py > '3'`
*   `CHECK.py >= '3.3'`
*   `CHECK.py('3.4')`
*   `CHECK.py <= '3.5'`
