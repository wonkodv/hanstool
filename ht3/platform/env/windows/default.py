from ht3.lib import Env

@Env
def gui_stay_on_top():
    Env.COMMAND_WINDOW.wm_attributes('-topmost', 1)
