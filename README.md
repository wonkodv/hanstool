TL;DR
-----

    sh: pip install git+https://github.com/wonkodv/hanstool
    sh: ht
    ht> ++ tools.80.py web
    vim
        @cmd(name="web")
        def web():
            execute("/usr/bin/firefox","http://example.com")
    ht> web
    ht>


HansTool 3
========


A third attempt, this time with python:)

The idea is, that a language that lets you quickly execute some commands (like bash)
is not a good language to write scripts, functions etc. with, so the HT3 splits this
into a command language that quickly executes arbitrary commands and python to write
what those commands do.

Components:
*   Commands have a name and execute things. Implemented as Python functions.
*   A simple Language in which you specify a command, possibly with Arguments.
    Looks very shell like. If there is no such command, you can choose what to do,
    for example evaluate it as python expression and show the result.
*   Script loader, which executes python scripts in which you define commands.
*   One global Namespace in which scripts can share common functions, variables, ...
*   Completion for Commands, their arguments, and simple python expressions or statements
*   Frontends: They ask the user for input, offer completion, show messages and
    can be controlled by commands.
*   Utillity functions.
    Depending on the executing os, a different set of
    functions is made available. For example in windows, there is the
    `MessageBox` function, taken right out of user32.dll, under linux, there isnt.
    There is a set of functions to simulate user input like moving the mouse, or
    Keystrokes. In (another) Minilanguage, you can specify those inputs easily.


Command
-----

Commands are the concept of python functions, executed by a short name.
For clarification:
*   command-string: The text (including Arguments) you type to execute a command
*   command-name: The text before any arguments you type to execute a command
*   command-arguments: The argument part of the command-string  you type to execute
    a command
*   command-function: The python function in which things happen
*   command-class: A Class for each command that knows the command name, function,
    argument parsing method, .... Instantiated with a command-string to give the
    command-object, which can be called once to execute the command function.
*   command-object: One invocation of a command.
*   command-attributes:  Attributes of the command (name, hotkey, ...). These are
    stored as Attributes of the command class


Command Strings
------

Anything before the first space of a command string is the command name, anything after the first
space is a command argument.

Examples of command names:

*   `web`
*   `doStuff`
*   `#`

Examples of commands, with and without arguments:

*   `web example.com`
*   `doStuff`
*   `# vim -c /Hans`
*   `& firefox http://example.com"

Command-Functions
---

Commands are python functions with some additional attributes. A python
function becomes a command-function by passing it to `cmd` or `cmd(kwargs)` usually in the form of a decorator.

    @cmd(name="e")
    def edit_file(file_name:Path, line:int=0):
        pass # invoke an editor for file_name at line

Note that, the function is stored itself under its own name in the script where it is defined.
The command class is stored under the command-name in the
`COMMANDS` dictionary, and does not appear anywhere else.
The command has the following properties:

*   Name is `e`. This would often be the function name, but can be different.
    Any sequence of printable, non-whitespace characters works.
*   Arguments to `e` are 1 Path and an int. The argument string will be parsed with
    `shlex.split()` to seperate the two arguments, converted to `pathlib.Path` and `int` and
    passes to the `edit_file` function.

Typing `e ~/todo 10` has mostly the same effect as the python expression
`edit_file(pathlib.Path("~/todo").expanduser(), 10)`

Argument Parsing Methods
-------------------------

There are multiple argument parsing strategies implemented, they can be chosen
with `@cmd(args=...)` the default, `auto`, choses automatically, based on the
function's signature:

*   if there is no parameter, no command-argument is allowed
*   if there is only parameter, the complete argument-string is passed as the single parameter
*   if there are multiple positional parameters, the argument-string is parsed with
    `shlex.split()`.

Argument Parsers are also respnsible for argument completion.

Different Argument parsing strategies are possible, see [Argument Parsing](./docs/ARGUMENTS.md)

The one unified Namespace `Env`
-------------------------------

Namespaces are very pythonic and you should always have more of those.  But putting many things in
the same namespace saves a lot of typing and allows to overwrite behavior in other places.
Env should be used by scripts to define, use
and overwrite functions and variables and share these among each other.  For example `edit_file` is
implemented in `common.10` to use the `EDITOR` variable, but can be overwritten in any script that
is loaded later to use an explicit editor.

`ht3.env.Env` is registered as its own module `Env`. It can be used to import its elements,
as a dcorator to put functions in Env, has an `updateable` decorator with which functions (like
`edit_file`) can be declared, referenced and later updated, with references beeing updated as well.

    @Env
    def some_func(): pass
    Env['PATH'] = foo

    X = 1
    def bar_baz(): pass
    Env.update(vars()) # add X and bar_baz (and some_func which is already there)

    @Env.updateable
    def foo(): return 1
    from Env import foo as f
    @Env.updateable
    def foo(): return 2
    assert f() == 2 # foo is updateable. you only hold wrappers that look up the newest function in Env


More in [Env](./docs/ENV.md)

Scripts
-----------

Scripts are python files that are imported as submodules of `Env`.
You can define functions variables and most importantly, commands there.
The way you load scripts:
1.  Specify one or more scripts or directories with scripts on the command line
2.  If no scripts were loaded on the command line,
    The ':' seperated directories from the `SCRIPTS` variable are loaded (from the
    `Env`. Use the `HT3_SCRIPTS` environment variable from outside ht3.)
3.  If no `SCRIPTS` variable is defined, use `ht3/default_scripts`
    which definitely exists and `~/.config/ht3` if exists.

Since `~/.config` looks a bit silly on windows, you might want to name
your script folder (and probably the default scripts) explicitly using the
1st or 2nd form from a batch file.

The order in which scripts are loaded matters if they overwrite things that
other scripts defined. Your scripts can for example redefine commands that
the default scripts already defined.

Scripts are added (`-s` argument) and loaded (`-l`). In the loading step,
all added scripts (and scripts in added directories) are sorted by a numeric
index before the `.py` suffix and by their name, not (!) by the order in which
they were added.
1.  W.10.py
2.  a.30.py
3.  b.30.py
4.  a.1.2.3.z.40.py
5.  a.py
6.  z.py
7.  v.110.py

The default scripts might change. If you dont like that, copy them to your
script directory and pass it explicitly.

Be sure to load a script that initializes your Env before any other.
This can be `basic.0.py` or something else.

A script can do `from Env import *` to have most functionality it needs already imported.

Scripts are imported as submodules of `Env`. `a.10.py` will be accessible as `Env.a`, (and of
course as Env['a']) and in `sys.modules['Env.a']`.

### Script Numbering
The shipped scripts use a numbering scheme, where some areas are reserved for use by
the (current or future) shipped scripts while all others can be used by user scripts
to modify, extend, ... or undo what the shipped scripts do
*   0-9:    Load and Populate `Env`
*   20-29:  Functions and Commands that operate on the HT
*   40-49:  Useful / exemplary commands

The user scripts can use the following areas:
*   10-19:  Modify Environment
*   30-39:  Modify Functions that operate on HT
*   50-99:  Functions commands, ...
*   100:    Unnumbered Scripts are assigned the sortkey 100
*   100..:  Meta stuff after all commands, functions, ... are already defined

The recommended use is to put your user scripts with numbering from the UserRange
in `~/.config/ht3`

### Extra scripts

The extra scripts in `/extra_scripts` are not loaded by default, as they are very specific.


Some Default Commands
-----------------

The default scripts define some commands for example:


    !                    Redo a command from the history by its number or starting text
    #                    Execute a Program and wait for completion.
    $                    Show output of a shell command.
    &                    Execute a Program and let it run in background.
    +                    Edit the location where a command or function was defined.
    ++                   Define a command in a script.
    :                    Test a fake-sequence after 500 ms.
    ;                    Execute a python statement.
    =                    Evaluate a python expression and show the result
    ?                    Show help on a command or evaluated python expression
    debug                Debug a Command using PDB. Uses the Console
    edit_file            Edit a file using EDITOR.
    exception_trace      Open the traceback of the latest exception in gvim [...]
    exit                 Quit with return code or 0.
    history              Search for a command in the history file.
    import               Import a module into Env.
    l                    List all commands.
    quit                 Quit with return code or 0.
    rand                 Copy a random number to the Clipboard.
    reload               Reload none, one or all Modules. Then reload all scripts.
    restart              Restart ht.
    timer                timer
    vb                   Open VirtualBox (the manager) or start a box with the name

Frontends
-----------

Any packet can be a HT-Fronend. The user chooses which one(s) to load on the commandline.

*   `ht3.cli`: This one is really almost a shell
*   `ht3.gui`: A little Window with a bigger log window
*   `ht3.hotkey`: (Probably runs paralell to anotherone)
    Systemwide hotkeys for some commands (specify the hotkey in
    `@cmd(attrs=dict(HotKey="Ctrl+F5"))` Currently only on windows
*   `ht3.htd`: a Daemon that listens on a socket for commands.
    Commands can be sent with `python -m ht3.client "command"
    Only on UNIX.
*   [Awesome WM Client](./docs/AWESOME.md): A piece of lua that runs `ht3.client`
*   more are easily implemented, see [Frontends](./docs/FRONTENDS.md)

Command Line Arguments and Startup Behavior
-----------

The initialization and actions of the ht3 can be programmed on the commandline and/or in
the scripts.  Each argument is either a shorthand that looks like an option, or executed as a python
statement.

Initialization Shorthands (and the code they represent):

    -s SCRIPT   Add one script (not executed yet)       add_scripts(SCRIPT)
    -s FOLDER   Add all *.py files in FOLDER            add_script(FOLDER)
    -l          Sort and Load all added scripts         load_scripts()
    -f FRONTEND Load a frontend (don't start it yet)    load_frontend(FRONTEND)
    -e KEY VAL  Define Static (survives reload)         put_static(KEY, VAL)
    -d          add ht3/default_script.py and load all scripts

Action Shorthands:

    -r          Run all loaded Frontends                run_frontends()
    -c COMMAND  Run a command                           run_command(COMMAD)
    -x CODE     Execute code

Before an Action Shorthand, all added scripts are loaded, `default_script` if none was added. After
an Action shorthand, no default actions are performed, unless an initialization command follows.
After Initialization, the following default actions are executed:

    1. ht3/default_script.py is added if no scripts were added
    2. all added but not loaded scripts are loaded
    3. if no frontend was added, ht3.cli is added
    4. frontends are run

Note: the only difference of executing code with -x or without is, that -x counts as an action so
there will be no default actions.

Frontends are started with -r or `run_frontends`. Execution then stops until the first frontend
exits which stops all other frontends. Then further commandline arguments are executed and
possibly, default actions start the frontends again. Just forget its there.

Normal invocations:

*   `ht`:   Load `default_script.py` and the cli
*   `ht -f ht3.gui -f ht3.hotkey -f ht3.daemon` Load `default_script.py` and some more frontends
*   `ht -s config.py` Load `config.py` which can then do all kinds of things.
*   `ht -c some_command` Load `default_script.py` (Default Actions 1 and 2 before Action Shorthands)
    and run the command `some_command`. Then quit.

Initialization Scripts
----------------------

If you do not want to configure everything on the commandline, a script can do the initialization,
by passing `-s initscript.py` to `ht` and calling `add_scripts` and `load_frontend` in the script:

It is probably a good idea to define `_SCRIPT_RELOAD = False` in module scope, so the reload command
does not add the scripts/frontends again.

By default, `ht3\default_script.py` is used as init script. It loads scripts from:

    - `ht3/default_scripts/`
    - `~/.config/ht3/`
    - all paths from `HT3_SCRIPTS` environment variable

Configure Things
---------------

Behavior of default commands can be configured via settings in `Env`, behavior of the HT-Core can
be configured via hooks. Hooks are lists of functions that are all called for notifications, or
that are called until the first function returns a useful result.

*   `COMMAND_NOT_FOUND_HOOK` is checked if there is no command with the name.
*   `general_completion(s)` should return a list/iterator of completions for
    the general input. The default is, to complete commands if possible, else
    python code. Default is to try to eval/exec as python or to start the programm.
*   `CLI_PROMPT`: the text in the CLI Prompt, can be a `str` or a callable
    returning strings. Default: `'ht3> '`
*   `EDITOR`: a list of strings that should be an editor with parameters.
    It is used by the `edit_file` function in the `default_scripts`.
*   `HISTORY`: a path to a file that contains the latest commands.
*   `HISTORY_LIMIT`: the number of entries to keep when loading the file
*   `DEBUG`: set to true to do post mortem pdb debugging. and more logging

The script `ht3\default_scripts\environment.3.py` loads all environment Variables that start with
`HT3_` into the env, without the prefix.

    export HT3_HISTORY=~/.config/ht3/readline_history
    export HT3_DEBUG=1
    export HT3_SCRIPTS=/opt/imported/scripts:~/__config/ht3

Thos will allways be string variables. Other python objects can be configured in scripts, or as
evaluated code on the commandline.

Tipps
-----

The `ht3.cli` uses readline. Configure it as you need.
    import readline
    readline.parse_and_bind('set editing-mode vi')

Make it more shell like by importing modules like `sh` [^2] or `plumbum` [^3]

[^2]: https://amoffat.github.io/sh/
[^3]: https://plumbum.readthedocs.org/en/latest/

Developing
----------

You are welcome to contribute, see [here](./docs/DEVELOPE.md).
