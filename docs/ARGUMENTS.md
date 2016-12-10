Argument Parsing
================

There are multiple argument parsing strategies implemented, they can be chosen with `@cmd(args=...)` the default, `auto`, choses 
automatically, based on the function's signature:

*   if there is no parameter, no command-argument is allowed
*   if there is only parameter, the complete argument-string is passed as the single parameter
*   if there are multiple positional parameters, the argument-string is parsed with
    `shlex.split()`.

These can be specified explicitly using `0`,`1` or `'shell'`.

If `args` starts with `:`, the argument-string is parsed by `getopt`, and passed to the function as
`**kwargs`.

Argument Conversion
--------------

Parameters can either be strings, or converted using annotations of the function parameter.
For example:

    def edit_file(file_name:Path, line:int=0):

The first argument is converted to a `Path`, the second to an `int`.
You can compose basic parameter types:
For example:

    def foo(i: args.Union(args.Int, args.Float, args.Option("a","b"),
            *b:args.Sequence(args.Int,args.Bool)))

3 arguments are expected, the first is converted to an Int, if that fails to a float, if that fails
it must be `'a'`or `'b'` and is passed to `i`.
The second argument must be an int and the third a bool. 2nd and 3rd arguments are passed ot the
parameter b.

valid:

    foo b 0 Yes
    foo 0.2e10 0xFF False

invalid:

    foo
    foo c 0 Yes
    foo 1 1 Hans


Argument completion
--------------
The annotated types of parameters are used to offer completion of arguments.


Parameter Type Annotations
----------------

Basic:

*   `Int`                   accepts 0xFF 0b11101 and so on
*   `Range`                 like `Int` but only in a range
*   `Float`
*   `Bool`                  Accepts Yes No False True 0 1 and so on
*   `Path`                  Filesystem Path, passed as `pathlib.Path`

Parameter types that pass the string without conversion, but perform completion or validation:
*   `Str`
*   `Python`                Python expression or statemens, passed as `str`
*   `Executable`            Executable in PATH or absolute, passed as String
*   `ExecutableWithArgs`    Executable plus arguments, passe as string that must be 
                            shell-split
*   `Command`               Name of a command
*   `CommandWithArgs`       Name and arguments of a command
*   `Option(options, ignore_case=False, sort=False, allow_others=False)`
                            Must match on of a list of strings. if `allow_others` the options
                            are only used for completion and any string is accepted

Composing Parameter types
*   `Union(*typs)`          One of several possible types, the first conversion that does not
                            throw a `ValueError` is used.

Parameters that Expect multiple Arguments (can only be used on (*args):
*   `Sequence(*typs)`       A list of positional arguments. The first has `typs[0]`,
                            the second `typs[1]` ...
*   `MultiParam(typ)`       A list of arguments of type `typ`

Make your own:
*   `Param(convert,complete,doc)` creates a param type that calls `convert` and `complete`.
                            All arguments are optional

shorthands:

*   Objects of type `int`, `float`, `bool`, `str`, `range`, `pathlib.Path` are converted to the respective ParamType
*   Sequence of strings are converted to an Option. The sequence is not copied so the current
    version for mutable sequences is used.
*   a function with `convert` in its name is converted to a `Param(convert=...)`
*   a function with `complete` in its name is converted to a `Param(complete=...)`

