The one unified Namespace `Env`
-------------------------------

`Env` is intended as a namespace in which scripts share useful stuff.
It is implemented in `ht3.env.Env` and registered as module `Env`.

Scripts can:

*   Set variables in Env:
        Env['FOO'] = 123
* Access variables in Env
        Env.FOO
        Env['FOO']

*   import bindings from Env:
        from Env import *
        from Env import execute

*   export all their bindings to `Env` using `update`:

        Env.update((k,v) for k,v in globals().items() if k[0] != '_')

*   add single functions to Env using

        @Env
        def func


When commands are executed, the latest result is stored in `Env['_']`, all Results in `Env['__']
and Exceptions in `Env['EXCEPTIONS']`.

Commands and Env are not dependant on each other. Overwriting in one does not influence in the
other.
