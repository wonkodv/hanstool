

def complete_executable_with_args(s):
    import shlex
    parts = shlex.split(s+"|")
    #TODO join with ShellArgs Code

    last = parts[-1][:-1]

    prefix = s[:len(s)-len(last)]

    exe = parts[0]

    if exe in []:
        pass # TODO: complete for exe
    else:
        compl = complete_path(last)

    for c in compl:
        yield prefix + c




@COMMAND_NOT_FOUND_HOOK.register
def _executable_command_h(s):
    import shutil
    try:
        parts = shlex.split(s)
    except ValueError:
        pass
    else:
        if shutil.which(parts[0]):
            return _procio, s
