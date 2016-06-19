

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

