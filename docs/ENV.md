The one unified Namespace `Env`
-------------------------------

All bindings are added by scripts.
In the default scripts, `basic.0.py` puts various ht3 control functions,
all of the utility functions, and some useful functions from the python libs
(`sleep`, `Path`, etc.) into Env, but you don't have to use that file.

Since anything that is defined in module scope of the scipts is put into the
namespace, it might be useful to wrap code that uses variables or imports
modules into a function with a name that does not annoy you later, or simply
deleting it once it was called. From inside, bindings in the Env can still be
made with the `global` keyword.

    def initialize_something_once():
        import some.module
        compute = something
        do_something()
        global ThisIsImportant
        ThisIsImportant = 42 # put this in Env
    initialize_something_once()
    del initialize_something_once

The Env can be reloaded, in which case it forgets everything except for a few
"persistent" bindings. These are made with `Env.put_persistent(key, value)`.

Elements in Env that are expected by `ht3` core code:

*   `command_not_found_hook(string)`
*   `general_completion`
*   `log`
*   `show`
*   `help`
*   `log_error`
*   `log_command`
*   `log_command_finished`
*   `log_thread_finished`
*   `log_subprocess`
*   `log_subprocess_finished`

Elements that are used by ht3 core code:

*   `SCRIPTS`
*   `DEBUG`
*   `CLI_PROMPT`
*   `CLI_HISTORY`
*   `GUI_HISTORY`
*   `SOCKET`

Elements that are set by core code:

*   `_` the result of the previous `run_command` if not `None`
