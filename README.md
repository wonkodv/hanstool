HansTool 3
========

A third attempt, this time with python:)

Tool that does things without typing much. Like a shell but less confusing
because you program your own stuff in python and start with a (mostly) clean NameSpace [1].

Components:
*   Commands have a name and execute things. Implemented as Python functions.
*   A simple Language in which you specify a command, possibly with Arguments.
    Looks very shell like. If there is no such command, interprete it as python.
*   Script loader, which executes python scripts in which you define commands.
*   One global Namespace in which the scripts and commands are exected in, for less typing
*   Completion for Commands, their arguments, and simple python statements
*   Frontends: They ask the user for input, offer completion and
    offer a few functions to the commands.
    *   CLI: This one is really almost a shell
    *   A little Window
    *   Hotkeys: (Probably runs paralell to anotherone) which has systemwide hotkeys for some commands
    *   Awesome WM Client: Like the MOD+R Prompt
    *   more are easily implemented
*   Plattform aware functions. depending on the executing os, a different set of 
    functions is made available in the Namespace. For example in windows, there is the
    `MessageBox` function, taken right out of user32.dll, under linux, there isnt.

[1]: I Once wrote a Shell script to do some things when i start my computer,
    e.g. start music, open firefox, mail and 3 terminals I called this script
    `as` so i would not have to type as much because I'm lazy. After some
    weeks, i had to compile something and it didnt work, but music started to
    play and 3 terminals opend because `gcc` invokes the assmebler which is
    called `as` because many people before me where just as lazy.
    I like clean namespaces.

Command
-----

Commands are the concept of python functions, executed by a short name.
for clarification:
*   command-string: The text (including Arguments) you type to execute a command
*   command-name: The text before any arguments you type to execute a command
*   command-arguments: The argumetn part of the command-string  you type to execute a command
*   command-function: The command function the python function in which things happen
*   command-wrapper: The wrapper arround the command-function. This wrapper
    takes command-arguments, parses them and then calls the command-function with the parsed arguments.
*   command-attribute:  Attributes of the command (name, hotkey, ...). These are stored as Attributes of the wrapper.


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

and as some examples

    foo
    foo bar
    foo         bar baz!
    |
    $ cat ~/txt | /dev/null
    < some/file.ht


Command-Functions
---


Commands are python functions with some additional attributes. A python function becomes a command-function
by passing it to `cmd(kwargs)(the function)` or `cmd(the function)` usually in the form of a decorator.

    @cmd(name='!', args='shell', **MoreKWArgs)
    def execute_things(program, *arguments)
        log("Executing Program %s with arguments %s",program, arguments)
        subprocess.execute(list(programm,*arguments))

The effect is something like:

    def execute_things(programm, *arguments):
        ...

    def wrapper(string)
        args = Parse_Shell_Args(string)
        execute_things(*args)

    wrapper.name='!'
    wrapper.__doc__ = "Invoke as '!', takes Shell Arguments" + execute_things.__doc__ + "Defined in some/file.py:line"
    wrapper.attr = MoreKWArgs
    COMMANDS['!'] = wrapper
    del wrapper

Note that, the function is stored itself under its own name in the namespace, not the wrapper.
The wrapper is stored under the command-name in the `COMMANDS` dictionary. The
wrapper does not apear anywhere else.


*   Name: Often the function name, but can be different. For Example:
    *   `ff` opens firefox
    *   `vb` opens virtualbox
    *   `vb xp` starts a specific virtualbox which has winxp in it.
    *   `mdel` deletes the currently playing Song from the playlist, saves that playlist
    *   `|` opens that one game where you lay out waterpipes. (cant remember what its called)
*   Argument Parsing Strategies:
    *   `0` no arguments (the default) the command `foo` results in the python statement
        `COMMANDS['foo']()`. If the name of the command is the same as the command-fucntion (default)
        this is equal to the python statement `foo()`. The examples below assume this.
    *   `1` passes the entire string that follows the command-name to the command-function
        `foo bar -baz="42'+3"   ` is the same as the python statement `foo('bar -baz="42\'+3"')`
        raises a value error if there is no argument (`foo` and `foo    `)
    *   `?` is like the above but does not raise an error
        `foo arg` makes `foo('arg')`
        `foo    ` makes `foo()`
    *   `shell` does shell like parsing (considering whitespaces and quotes, no variable expansion)
        `foo bar "baz " "'5 + "4'2'` makes `foo("bar", "baz", "5 + 42")
    *   `getopt` to make things very shell like, if you know what getopt is, there 
        will be no suprises for you there, if not, you better stay away from it.
    *   `getlongopt` like `getopt` but even more so.
    *   `set` like `1` but has to be one of a set of args
    *   `dict` like `set` but has to be a key of a dictionary. The lookup value is passed to the fucntion
    *   `path` like `1`. Must be an absolute or relative (to the current dir) path. Is passed as a Path object.
    *   a callable like `int` or `float`: will take the entire string pass it through the function an pass result as the 1 argument.
*   Function: A Command-function is a normal python function with a `cmd` decorator. The decorator
    takes some optional keyword arguments with which you specify:
    *   Name: defautls to the function Name
    *   args: defines, how a the argument part of the command-string is parsed and passed on to the command-function.
    *   more kwargs that are passed to the Argument parser
    *   more kwargs that become attributes of the command, which can be scanned by other componentes (e.g. Hotkeys, ...)


The one unified Namespace `Env`
-------------------------------

Namespaces are very pythonic and you should allways have more of those.  But
this tool is not about clean and readable code, it's about getting things done
(without dolores -.-) therfore there is only one great namespace in which
scripts and commands are executed. From outside that namespace (the core code
and plattform modules) the environment is available in `ht3.lib.Env`. Env is a
decorator to put functions in it, its a dictionary kind of thing and it is also
a namespace.
    @Env
    def foo(): pass
    Env['foo']
    Env.foo()
Env contains itself if you need to use it from your scripts or commands.

This gets problematic if you define stuff on module level in your script,
use it from your command and another script uses different things with the same
name on module level. But it still beats `bash` ([1]).



Some Default Commands
-----------------

*   `!` executes programms. `! gvim ~/txt` opens txt in gvim.
    The `!` comand has argument parsing strategy `shell` so the command-function
    is invoked with 2 arguments, the strings `gvim` and `~/txt`. It
    executes the first one, an passes the second as argument. gvim
    has to deal with he tilde character. Since vim is awesome, this works. If you
    used this with notepad.exe, which is not awesome, it would not work.
*   `$` calls the Shell. `$ wc -l ~/txt > ~/txt-len` writes the length of txt to txt-len
    The `$` command has argumennt parsing `1` because the function wants the entire
    text after the dolalr sign, open a shell, and let that shell figure out what to
    do with the string.
*   `l` List all commands
*   `exit` Close the tool
*   `;` execute a python statement, e.g. `; for i in 1,2,3,4: show(i**2)`
*   `=` evaluate and print a python statment: `= 1+1*1+1`
*   '?' help on commands or python objects: `? exit` `? sys`


Frontends
-----------

Any packet can be a HT-Fronend. The user chooses which one(s) to load.

A Frontend must specify at module level:
*   a `loop()` method. This is called from a frontend specific thread and should start the frontend and ask
    the user for input. Place a REPL's while loop or a GUI's MessagePump in
    this function. If the user closes the frontend, `loop should return and
    further stuff may happen. Raise `SystemExit` to stop the program.
*   a `stop()` function which is called from the main thread and should notify the `loop function to return soon.
    this may be called after `loop` returned.

At least one Frontend should put the following functions in `Env`:
*   `show(text, *args, **kwargs)` put `text%args` to the users attention (Notification, Messagebox, print, ...)
*   `log(text, *args, **kwargs)` put `text%args` somewhere the user can look it up. (TextArea in some window, print, ...)
*   `edit_file(path, line)` Open an Editor for the file `path`, possibly at `line`.
*   `help(topic)` Display help on a command or python topic (Invoke `less`, display a large text window, ...)
*   `handle_exception` Tell the user a command or Frontend or ... did something bad.

A Frontend should propably provide a function (decorator) so scripts can register functions
that are executed at the start of the frontend's `loop` after some initialization happened.

Frontends should mainly call the following functions from `ht3.lib`:
*   `run_command(string)`   to do what the user typed
*   `get_completion(string)` to complete what the user started to type

Frontends can get information (names, doc, hotkey, ...) about registered commands from `ht3.lib.COMMANDS`


Configure Things
---------------

Some Behaviour can be configured by setting things in the `Env`.
*   `command_not_found_hook` is executed if the command-string does
    not specify a command. Defaults to evaluating or executing as python code.
*   `CLI_PROMPT()`: the text in the CLI Prompt, defaults to `lambda:'ht3> '`
*   `RL_HISTORY`: a string that points to a file with the history of the repl.

Strings can be configured via environment, but require a `HT3_` prefix, for
example in `.bashrc`:
    export HT3_RL_HISTORY=~/.config/hanstool/readline_history
Other python objects and strings can be configured in scripts. The default
values are set very early by `ht3.lib`. Scripts are run in the order they appear on
the command line.

Command Line
-----------

Execute with `python3 -m ht ARGUMENTS` where arguments are zero or more of the following:
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
frontends. When processing `-r`, all the frontends that were loaded by
previous `-f` are started.  Once one interface exits, all others are stopped as
well and the argument after `-r` is processed.  Multiple `-r` will start
the frontends multiple times. At the end, if there was `-f` but not `-r` the frontends are started.
If there was no `-f` and no `-x`, the `ht3.cli` frontend is started.

Tipps
-----

The `ht3.cli` uses readline. Configure it as you need.
    import readline
    readline.parse_and_bind('set editing-mode vi')

Make it more shell like by importing modules like `sh` [2] or `plumbum` [3]
into your Environment and glue them to the `command_not_found_hook`.


[2]: https://amoffat.github.io/sh/
[3]: https://plumbum.readthedocs.org/en/latest/
