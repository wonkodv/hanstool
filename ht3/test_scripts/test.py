"""A set of commands that test if scripts and commands work as expected."""

from Env import *


@cmd
def test(silent: args.Bool = False):
    test_assertions_enabled()
    test_script_order()
    test_script_module()
    test_argument_parsing()
    test_decorator()
    test_names()

    if not silent:
        print("Test OK")

    return "Integration Tests ran"


# Assertions

def test_assertions_enabled():
    try:
        assert False
    except AssertionError:
        pass
    else:
        raise Exception("Who runs a Test suite with Assertions disabled?")

# Script Order


def test_script_order():
    # The scripts were ordered.
    # no index alphabetical after high index after low index
    #   init.0.py
    #   overwrited.5.py
    #   overwriteb.10.py
    #   overwritea.py
    #   overwritec.py
    #   test.py
    # And scripts run in the same namespace

    assert Env['SCRIPT_ORDER'] == ['init', 'd', 'b', 'a', 'c']


def test_script_module():
    assert __name__ == 'Env.test'

    import importlib
    mod = importlib.import_module('Env.test')
    assert mod.test_script_module is test_script_module
    test_script_module.__module__ == 'Env.test'

# @cmd


@cmd
def decorator_noargs_dummy():
    pass


@cmd()
def decorator_args_dummy():
    pass


def test_decorator():
    # decorative decorator decorated correctly
    assert COMMANDS['decorator_noargs_dummy'].target is decorator_noargs_dummy
    assert COMMANDS['decorator_args_dummy'].target is decorator_args_dummy


# Args

ARG_TEST = []


@cmd
def shellargtest(*args):
    ARG_TEST.append(args)


@cmd
def autoargtest(i: int, b: bool, *arr: args.Union(int, float, bool, str)):
    ARG_TEST.append(i)
    ARG_TEST.append(b)
    ARG_TEST.append(arr)


def test_argument_parsing():
    ARG_TEST.clear()
    run_command("""shellargtest 1 "2" '3'""")
    run_command("""shellargtest""")
    run_command("""shellargtest "a b c d" """)
    assert ARG_TEST == [('1', '2', '3'), (), ('a b c d',)]
    ARG_TEST.clear()
    run_command("""autoargtest 1 Yes 0 1.1 Yes No Yes Hans 1""")
    assert ARG_TEST[0] == 1
    assert ARG_TEST[1] is True
    assert ARG_TEST[2] == (0, 1.1, True, False, True, 'Hans', 1)


# Name

@cmd(name='$IsValid!')
def name_test():
    global NAME_TEST
    NAME_TEST = True


def test_names():
    global NAME_TEST
    NAME_TEST = False
    run_command('$IsValid!')
    assert NAME_TEST
