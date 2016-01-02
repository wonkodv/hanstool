Argument Parsing
================

You select kind of argument parsing your command uses by passing its name in
the `args` parameter of `@cmd`. Some Argument parsers need additional arguments
that are passed as keyword argument to `@cmd`.

*   `0` `None` or `False`: no arguments. The command `foo` results in the python statement
    `COMMANDS['foo']()`. Raises an error if the argument has any non whitespace chars.
*   `1` or `'all'`: passes the entire string that follows the command-name to the
    command-function `foo bar -baz="42'+3"   ` is the same as the python statement
    `foo('bar -baz="42\'+3"')` raises a value error if there is no argument.
*   `?` is like `1` but does not raise an error
    `foo arg` makes `foo('arg')`
    `foo` makes `foo()`
*   `shell` does shell like parsing (considering whitespaces and quotes,
    no variable expansion)
    `foo $bar "baz " "'5 + "4'2'` makes `foo("$bar", "baz", "5 + 42")
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

