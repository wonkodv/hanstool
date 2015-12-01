from . import Env

@Env
def command_not_found_hook(s):
    """ Try to evaluate as expression and return the result,
        if that fails, try to execute as statements """
    try:
        c = compile(s, "<input>", "eval")
    except SyntaxError:
        c = compile(s, "<input>", "exec")
    return eval(c, Env.dict)

@Env
def handle_exception(e):
    """ Handle Exceptions that a frontend can not handle itself """
    if Env.get('DEBUG',False):
        import pdb
        pdb.post_mortem()
    traceback.print_exc()

