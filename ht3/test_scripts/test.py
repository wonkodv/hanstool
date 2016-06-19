"""A set of commands that test if scripts and commands work as expected."""

@cmd
def test(silent:args.Bool=False):

    test_assertions_enabled()
    test_script_order()
    test_argument_parsing()
    test_decorator()
    test_names()

    if not silent:
        print ("Test OK")

    @cmd
    def test(*a):
        raise NotImplementedError("Don't run test twice")

    return "Integration Tests ran"

#### Assertions

def test_assertions_enabled():
    try:
        assert False
    except AssertionError:
        pass
    else:
        print("Who runs a Test suite with Assertions disabled?")
        raise SystemExit(1)

#### Script Order

def test_script_order():
    # The scripts were ordered.
    # high index after low index after no index alphabetical
    #   overwritea.py
    #   overwriteb.10.py
    #   overwritec.py
    #   overwrited.5.py
    #   test.py
    # And scripts run in the same namespace
    assert Env['OVERWRITE'] == [0, 1, 2, 3]


#### @cmd

@cmd
def decorator_noargs_dummy():
    pass

@cmd()
def decorator_args_dummy():
    pass

def test_decorator():
    # decorator decorates correctly
    assert COMMANDS['decorator_noargs_dummy'].function is decorator_noargs_dummy
    assert COMMANDS['decorator_args_dummy'].function is decorator_args_dummy


#### Args

ARG_TEST = []
@cmd
def argtest(*args):
    ARG_TEST.append(args)

def test_argument_parsing():
    run_command("""argtest 1 "2" '3'""")
    run_command("""argtest""")
    run_command("""argtest "a b c d" """)
    assert ARG_TEST == [('1','2','3'), (), ('a b c d',)]


#### Name

NAME_TEST=False
@cmd(name='$IsValid!')
def name_test():
    global NAME_TEST
    NAME_TEST=True

def test_names():
    run_command('$IsValid!')
    assert NAME_TEST
