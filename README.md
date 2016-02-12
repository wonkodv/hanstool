TL;DR
-----

    sh: pip install git+https://github.com/wonkodv/hanstool
    sh: ht
    ht> ++ tools.80.py web
    vim
        @cmd(name="web")
        def web():
            execute("/usr/bin/firefox")
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
*   One global Namespace in which the scripts and commands are exected in, for less typing
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
for clarification:
*   command-string: The text (including Arguments) you type to execute a command
*   command-name: The text before any arguments you type to execute a command
*   command-arguments: The argumetn part of the command-string  you type to execute
    a command
*   command-function: The command function the python function in which things happen
*   command-wrapper: The wrapper arround the command-function. This wrapper
    takes command-arguments, parses them and then calls the command-function with
    the parsed arguments.
*   command-attribute:  Attributes of the command (name, hotkey, ...). These are
    stored as Attributes of the wrapper.


Command Strings
------

The String you type to get things done as EBNF:

    COMMAND:    NAME
    COMMAND:    NAME WS+ ARGUMENT
    COMMAND:    Python Expression
    COMMAND:    (Python Statement)+
    NAME:       (~(WS RETURN))+
    WS:         SPACE | TAB
    ARGUMENT:   (~RETURN)+

and as plain text:

    all (printable) characters that are not whitespaces make the command name, the rest
    of the line is the argument to the command

and as some examples:

    web
    web example.com
    ? web
    foo
    foo bar
    foo         bar baz!
    foo -bar --baz=42
    : +SHIFT A -SHIFT
    |
    $ cat ~/txt | /dev/null
    < some/file.ht


Command-Functions
---

Commands are python functions with some additional attributes. A python
function becomes a command-function by passing it to `cmd(kwargs)(the
function)` or `cmd(the function)` usually in the form of a decorator.

    @cmd(name='!', args='shell', **MoreKWArgs)
    def execute_things(program, *arguments)
        log("Executing Program %s with arguments %s",program, arguments)
        subprocess.execute(list(programm,*arguments))

The `@cmd` decorator has more or less the following effect:

    def execute_things(programm, *arguments):
        log("Executing Program %s with arguments %s",program, arguments)
        subprocess.execute(list(programm,*arguments))

    def wrapper(string)
        args = Parse_Shell_Args(string)
        execute_things(*args)

    wrapper.name='!'
    wrapper.__doc__ = "Invoke as '!', takes Shell Arguments" + execute_things.__doc__ + "Defined in some/file.py:line"
    wrapper.attr = MoreKWArgs
    COMMANDS['!'] = wrapper
    del wrapper

Note that, the function is stored itself under its own name in the namespace,
not the wrapper.  The wrapper is stored under the command-name in the
`COMMANDS` dictionary. The wrapper does not appear anywhere else.
The command has the following properties:

*   Name is `!`. This would often be the function name, but can be different.
    Any sequence of printable, non-whitespace characters works.
*   Arguments to `!` should be parsed with the `shell` strategy. The complete text
    after `!` is parsed into a list of strings in the way unix shells parse
    argument strings. (see doc of `shlex.split()` for details.)
*   Function: The `execute_things` function will be called when the user runs the `!`
    command. The command-argument is parsed and passed to the function as
    positional arguments. For example the following commands are equal to the python calls:
    *   `! a b "c"` =>  `execute_things('a', 'b', 'c')`
    *   `! ` =>  `execute_things()`
    *   `! rm -rf /` =>  `execute_things('rm', '-rf', '/')`

Argument Parsing Methods
-------------------------

There are multiple argument parsing strategies implemented.
The default one does shell like parsing and passes the strings as positional
arguments to your function. If the parameters are annotated, that annotation
should be a callable that converts a string into your expected type (like `int` or `float`).

More in [Argument Parsing](./docs/ARGUMENTS.md)

The one unified Namespace `Env`
-------------------------------

Namespaces are very pythonic and you should always have more of those.  But
this tool is not about clean and readable code, it's about getting things done
(without dolores -.-) therefore there is only one great namespace in which
scripts and commands are executed. From outside that namespace (the core code
and platform modules) the environment is available in `ht3.env.Env`.


More in [Env](./docs/ENV.md)

Scripts
-----------

Scripts are python scripts that are all executed in the same namespace.
You can define functions variables and most important, commands there.
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

Inside a directory, scripts are sorted by a numeric index before the `.py` suffix.
1.  a.py
1.  z.py
2.  W.10.py
3.  a.30.py
4.  b.30.py
5.  a.1.2.3.z.40.py

The default scripts might change. If you dont like that, copy them to your
script directory and pass it explicitly.

Be sure to load a script that initializes your Env before any other.
This can be `basic.0.py` or something else.

If one of your scripts imports `ht3.check.CHECK`, you can make your scripts flexible
for running on different plattforms and with different frontends.
See [CHECK](./docs/CHECK.md).

Some Default Commands
-----------------

The default scripts define some commands:

*   `l` List all commands
*   `exit` Close the tool
*   `=` evaluate a python statment and show the result: `= 1+1*1+1`
*   `;` execute a python statement, e.g. `; for i in 1,2,3,4: show(i**2)`
*   `?` help on commands or python objects: `? exit` `? sys`
*   `+` open the editor where a command or other function was defined
*   `++ s [c]` open the script that matches `s` or a new script named `s`.
    If given, add template for a new command named `c`
*   `$` calls the Shell. `$ wc -l ~/txt > ~/txt-len` writes the length of txt to txt-len
    The `$` command has argumennt parsing `1` because the function wants the entire
    text after the dolalr sign, open a shell, and let that shell figure out what to
    do with the string.
*   `!` executes programms. `! gvim ~/txt` opens txt in gvim.
    The `!` comand has argument parsing strategy `shell` so the command-function
    is invoked with 2 arguments, the strings `gvim` and `~/txt`. It
    executes the first one, an passes the second as argument. `gvim`
    has to deal with he tilde character. Since vim is awesome, this works. If you
    used this with notepad.exe, which is not awesome, it would not work.
    Note that on windows, argument parsing can be rather weird, for example
    `! explorer "/select,C:\Program Files\Notepad++\Notepad++.exe"` does not work
    but `$ explorer /select,"C:\Program Files\Notepad++\Notepad++.exe"` works.
*   `#` open the target command's file in explorer. If you have a command that
    executes "notepad++", the `# n++` command would open explorer with the
    notepad++.exe selected.  Works by inspecting the code of a command function
    and taking the first string constant names an existing file. Only on
    windows.

Frontends
-----------

Any packet can be a HT-Fronend. The user chooses which one(s) to load on the commandline.

*   CLI: This one is really almost a shell
*   A little Window
*   Hotkeys: (Probably runs paralell to anotherone) which has
    systemwide hotkeys for some commands
*   a Daemon: listens on a socket for commands. commands can be sent with
    `python -m ht3.client "command 1" "command 2"`.
    Only on UNIX.
*   [Awesome WM Client](./docs/AWESOME.md): A piece of lua that runs `ht3.client`
*   more are easily implemented, see [Frontends](./docs/FRONTENDS.md)


Command Line
-----------

The HT3 entry point is `ht3.__main__` so you can run it with `python -m ht3`.
when installing with `pip`, a script named `ht` is added to your `PATH` to do that.

You can pass any number of the following arguments:
*   `--help`        Display this text
*   `-e KEY VALUE`  add a variable to the environment
*   `-s FILE`       execute a script
*   `-s PATH`       execute a folder full of scripts. Scripts are sorted (z.10.py before a.20.py)
*   `-f FRONTEND`   load a frontend.
*   `-x COMMAND`    execute a command
*   `-r`            (run) Start all frontends loaded so far.
Arguments are processed in the order they are passed. You should propably put
them in the order they appear above to put things in the environment, then load
scripts, then load frontends, then execute some commands and finally start the
frontends. When processing `-r`, all the frontends that were loaded by previous
`-f` are started.  Once one interface exits, all others are stopped as well and
the argument after `-r` is processed.  Multiple `-r` will start the frontends
multiple times.

After processing all passed arguments, the following default actions happen:

*   If no script was loaded with `-s`:
    *   If there is an `Env.SCRIPTS` the scripts from there are loaded (
        multiple paths are seperated by `:`)
    *   else, the `default_scripts` are loaded and, if exists, the scripts from
        `~/.config/ht3`
*   If one or more frontends were loaded with `-f` but not run with `-r`,
    they are run.
*   If no frontend was loaded with `-f` and no command executed with `-x`, then
    the `ht3.cli` frontend is loaded and run.

It should usually be enough to just call `ht` without arguments, or with `-f`.

Configure Things
---------------

Some Behaviour can be configured by setting things in the `Env`.
*   `command_not_found_hook(s)` is executed if the command-string does
    not specify a command. Defaults to evaluating or executing as python code.
*   `general_completion(s)` should return a list/iterator of completions for
    the general input. The default is, to complete commands if possible, else
    python code.
*   `CLI_PROMPT`: the text in the CLI Prompt, can be a `str` or a callable
    returning strings. Default: `'ht3> '`
*   `EDITOR`: a list of strings that should be an editor with parameters.
    It is used by the `edit_file` function in the `default_scripts`.
*   `RL_HISTORY`: a string that points to a file with the history of the CLI repl.
*   `GUI_HISTORY`: a string that points at a file for the history of the GUI
    command window.
*   `DEBUG`: set to true to do post mortem pdb debugging.
*   `SCRIPTS` If no script is passed on the command line, this variable can specify
     scripts, seperated by `:` that will be loaded.

String variables can be configured via environment, but require a `HT3_` prefix, for
example in `.bashrc`:
    export HT3_RL_HISTORY=~/.config/ht3/readline_history
    export HT3_DEBUG=1
    export HT3_SCRIPTS=/opt/imported/scripts:~/__config/ht3
Other python objects and strings can be configured in scripts. The default
values are set very early by `ht3.lib`. Scripts are run in the order they appear on
the command line.


Tipps
-----

The `ht3.cli` uses readline. Configure it as you need.
    import readline
    readline.parse_and_bind('set editing-mode vi')

Make it more shell like by importing modules like `sh` [^2] or `plumbum` [^3]
into your Environment and glue them to the `command_not_found_hook`.
If you have a good setup, tell me about it!

[^2]: https://amoffat.github.io/sh/
[^3]: https://plumbum.readthedocs.org/en/latest/

Developing
----------

You are welcome to contribute, see [here](./docs/DEVELOPE.md).
