from Env import EXECUTABLE_W_ARGS_COMPLETE_HOOK, which, CHECK, exe_completer

if which('ls'):
    @exe_completer('ls')
    def complete_ls(parts):
        if parts[-1] == '-':
            for f in 'lrst10':
                yield '-' + f
            return True
