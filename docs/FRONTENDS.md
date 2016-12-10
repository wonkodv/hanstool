FRONTENDS
=========

You can easily implement a new Frontend by making a module that has these functions:
*   `start()`: This is called from the main thread and should emsure that the frontend
    is ready to run.
*   `loop()`: This is called from a frontend specific thread and
    should start the frontend and ask the user for input. Place a REPL's while
    loop or a GUI's MessagePump in this function. If the user closes the
    frontend, `loop` should return and further stuff may happen. Raise
    `SystemExit` to stop the program.
*   `stop()`: function which is called from the main thread and should notify
    the `loop` function to return soon. This function is also called if `loop` already
    returned.

You can use a `threading.Event` that is cleared in `start`, waited on in
`loop` and set by `stop`.

Frontends can get information (names, doc, hotkey, ...) about
registered commands from `ht3.command.COMMANDS`

Frontends should mainly call the following functions:
*   `ht3.command.run_command(string)` to do what the user typed.
*   `ht3.complete.get_completion(string)` to complete what the user started to type.
*   Register function to the Logging Hooks


Some functions may be useful to put into the `Env`:
*   Frontends should have an `__all__` tuple of functions that will be put in `Env`.

