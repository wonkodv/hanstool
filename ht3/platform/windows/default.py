from ... import lib

@lib.Env
def gui_stay_on_top():
    Env.COMMAND_WINDOW.wm_attributes('-topmost', 1)
