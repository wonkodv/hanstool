from . import command
from . import env

def complete_all(string):
    comp = complete_command(string) + complete_py(string)
    return comp

def complete_command(string):
    cmd, sep, args = command.parse_command(string)
    COMMANDS = command.COMMANDS

    if sep and cmd in COMMANDS: # only complete args if the space after command came already
        c = COMMANDS[cmd]
        values = c.complete(args)
        l = len(args)
        values = filter(lambda x:x[:l]==args, values)
        values = sorted(values)
        values = [cmd + sep + x for x in values]
    else:
        l = len(string)
        values = COMMANDS.keys()
        values = filter(lambda x:x[:l]==string, values)
        values = sorted(values)
    return values

def complete_py(string):
    #s = re.split("[^a-zA-A0-9_.]", string)
    #string = s[-1]
    parts = string.split(".")

    values = dict()
    values.update(__builtins__)
    values.update(env.Env.dict)

    if len(parts) == 1:
        pl = parts[0]
    else:
        p0 = parts[0]
        pl = parts[-1]

        try:
            val = values[p0]

            for p in parts[1:-1]:
                p = p.strip()
                val = getattr(val, p)

            values = dir(val)

            if hasattr(val, '__class__'):
                values.append('__class__')
                c = val.__class__
                while c != object:
                    values += dir(c)
                    c = c.__base__
        except:
            pass

    l = len(pl)
    prefix = string[:len(string)-l]

    values = filter(lambda x:x[:l]==pl, values)
    values = sorted(values)
    values = [prefix + x for x in values]

    return values

