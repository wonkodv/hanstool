import os.path

@cmd
def txt():
    execute(EDITOR,os.path.expanduser("~/txt"))
