from .lib import COMMANDS, Env, parse_command

def get_completion(string):
    c, args = parse_command(string)
    if c in COMMANDS:
        cmd = COMMANDS[c]
        values = cmd.arg_parser.complete(args)
        return [c+" "+ x for x in values]


    return command_completion(string) + py_completion(string)

def command_completion(string):
    l = len(string)
    return [ c for c in COMMANDS if c[:l]==string]

def py_completion(string):
    parts = [s.strip() for s in string.split(".")]

    values = dict()
    values.update(__builtins__)
    values.update(Env.dict)

    if len(parts) == 1:
        prefix = ""
        pl = string
    else:
        p0 = parts[0]
        pl = parts[-1]

        val = values[p0]

        for p in parts[1:-1]:
            val = getattr(val, p)

        values = dir(val)

        if hasattr(val, '__class__'):
            values.append('__class__')
            c = val.__class__
            while c != object:
                values += dir(c)
                c = c.__base__

    l = len(pl)
    prefix = string[:-l]

    return [ prefix + c for c in values if c[:l]==pl ]
