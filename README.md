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
    *   Hotkeys: (Probably runs paralell to anotherone) which has
        systemwide hotkeys for some commands
    *   Awesome WM Client: Like the MOD+R Prompt (Coming real soon)
    *   more are easily implemented
*   Plattform aware functions. depending on the executing os, a different set of 
    functions is made available in the Namespace. For example in windows, there is the
    `MessageBox` function, taken right out of user32.dll, under linux, there isnt.

[1]: I Once wrote a Shell script to do some things when i start my computer,
    e.g. start music, open firefox, mail and 3 terminals I called this script
    `as` instead of `auto_start`, so I would not have to type as much because
    I'm lazy. After some weeks, I had to compile something and it didnt work,
    but music started to play and 3 terminals opend. `gcc` invokes the
    assmebler which is called `as` because many people before me where just as
    lazy. Now I like clean namespaces.

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

and as plaintext:

    all (printable) characters that are not whitespaces make the command name, the rest
    of the line is the argument to the command

and as some examples:

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
`COMMANDS` dictionary. The wrapper does not apear anywhere else.
The command has the following properties:

*   Name is `!`. This would often be the function name, but can be different.
    Any sequence of printable, non-whitespace characters works.
*   Arguments to `!` should be parsed with the `shell` strategy. The complete text
    after `!` is parsed into a list of strings in the way unix shells parse
    argument strings. (see docu of `shlex.split()` for details.)
*   Function: The `execute_things` function will be called when the user types runs the `!`
    command. The command-argument is parsed and passed to the function as 
    positional arguments. For example the following commands are equal to the python calls:
    *   `! a b "c"` =>  `execute_things('a', 'b', 'c')`
    *   `! ` =>  `execute_things()`
    *   `! rm -rf /` =>  `execute_things('rm', '-rf', '/')`

Argument Parsing Methods
-------------------------

There are multiple argument parsing strategies implemented.
You select which one your command uses by passing its name in the `args` parameter of
`@cmd`. Some Argument parsers need additional arguments that are passed as keyword
argument to `@cmd`.

*   `0` `None` or `False`: no arguments. The command `foo` results in the python statement
    `COMMANDS['foo']()`. Raises an error if the argument has any non whitespace chars.
    this is equal to the python statement `foo()`. The examples below assume this.
*   `1` or `'all'`: passes the entire string that follows the command-name to the
    command-function `foo bar -baz="42'+3"   ` is the same as the python statement
    `foo('bar -baz="42\'+3"')` raises a value error if there is no argument
    (`foo` and `foo    `)
*   `?` is like `1` but does not raise an error
    `foo arg` makes `foo('arg')`
    `foo    ` makes `foo()`
*   `shell` does shell like parsing (considering whitespaces and quotes,
    no variable expansion)
    `foo bar "baz " "'5 + "4'2'` makes `foo("bar", "baz", "5 + 42")
*   `getopt` to make things very shell like.
    Pass the options in `opt` or, prefixed with `:`, directly in `args`.
    Note that options without a value, or where you explicitly pass a value of
    `''` are counted and passed as int, so multiple occurences are fine,
    options with value may occur only once. GNU style is used, so non-opt
    arguments and opt-arguments can be mixed.  The options are passed as kwargs
    so an option of `a:b` and args `-b spam -a bacon -bbb eggs` will result in the
    python call `function('spam', 'eggs', a='bacon', b=4)`
*   `set` with a set in `set` or many in `sets`. Like `1` but only arguments in the set(s)
    are accepted.
*   `dict` like `set` but has to be a key of a dictionary. The lookup value
    is passed to the fucntion. The dictionary(s) are passed as `dict` or `dicts`
*   `path` like `1`. Must be an absolute or relative (to the current dir) path.
    Is passed as a Path object.
*   `call`: with a callable like `int` or `float` in `call` will take the entire
    string pass it through the function an pass result as the single argument.
*   `auto` This is the default. It is like `shell` but uses the annotation of function
    arguments as callables to convert the argument, or str if there is no annotation.
    `foo(i:int, p:pathlib.Path)` will accept exactly 2 arguments, the first is passed
    through `int` and the second is made a `Path` before passing to the command-function.

The argument parsers `set`, `dict` and "callable" accept a `default` which is used
if the argument string is empty or only whitespaces. They do not use the fucntion
parameter default value from the function signature.

Instead of the name of an argparser, the `args` of `@cmd` can be:
* a dict (an instance of collections.abc.Mapping)
* a set (an instance of collections.abc.Container)
* a string starting with `:` for getopts
* a callable

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

Scripts
-----------

Scripts are python scripts that are all executed in the same namespace.
You can define functions variables and most important, commands there.
The way you load scripts:
1.  Specify one or more scripts or directories with scripts on the commandline
2.  If no scripts were loaded on the commandline,
    The ':' seperated directories from the `SCRIPTS` variable are loaded (from the
    `Env`. Use the `HT3_SCRIPTS` environment variable from outside ht3.)
3.  If no `SCRIPTS` variable is defined, use `ht3/default_scripts`
    which definitely exists and `~/.config/ht3` if exists.

Since `~/.config` looks a bit silly on windows, you might want to name
your script folder (and propably the default scripts) explicitly using the
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

Some Default Commands
-----------------

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
*   `help(topic)` Display help on a command or python topic (Invoke `less`, display a large text window, ...)
*   `handle_exception` Tell the user a command or Frontend or ... did something bad.

A Frontend should propably provide a function (decorator) so scripts can register functions
that are executed at the start of the frontend's `loop` after some initialization happened.

Frontends should mainly call the following functions:
*   `ht3.command.run_command(string)`   to do what the user typed
*   `ht3.complete.get_completion(string)` to complete what the user started to type

Frontends can get information (names, doc, hotkey, ...) about registered commands from `ht3.lib.COMMANDS`


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
*   `command_not_found_hook` is executed if the command-string does
    not specify a command. Defaults to evaluating or executing as python code.
*   `CLI_PROMPT()`: the text in the CLI Prompt, defaults to `lambda:'ht3> '`
*   `EDITOR`: a list of strings that should be an editor with parameters.
    It is used by the `edit_file` function in the `default_scripts`.
*   `RL_HISTORY`: a string that points to a file with the history of the repl.
*   `DEBUG`: set to true to do post mortem pdb debugging and show traces with all
        `log` and `show` messages
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

Make it more shell like by importing modules like `sh` [2] or `plumbum` [3]
into your Environment and glue them to the `command_not_found_hook`.


[2]: https://amoffat.github.io/sh/
[3]: https://plumbum.readthedocs.org/en/latest/


TEST
-----

[![Build Status](https://travis-ci.org/wonkodv/hanstool.svg)](https://travis-ci.org/wonkodv/hanstool)

There is a set of `unittest.TestCase` unit tests `test` that can be run with
`python -m unittest` or `py.test` or other `unittest`-compatible test runners.

There is also an integration test using `test_scripts` which defines some
commands which can be run (once) with the `test` command to test that they were registered
in the expected way.

Use `test` command to quickly run the integration test:

    python -m ht3 -s ht3/test_scripts -x test
