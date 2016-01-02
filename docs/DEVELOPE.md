Develope
========

To get started, do:

    git clone ssh://github.com/wonkodv/hanstool hanstool
    pip install --user --edit hanstool

Test
====

[![Build Status](https://travis-ci.org/wonkodv/hanstool.svg)](https://travis-ci.org/wonkodv/hanstool)

There is a set of `unittest.TestCase` unit tests in `test_*.py` files, next to the
modules which that can be run with `python -m unittest` or `py.test` or
other `unittest`-compatible test runners.

There is also an integration test using `test_scripts` which defines some
commands which can be run with the `test` command to test that they were registered
in the expected way.

    python -m ht3 -s ht3/test_scripts -x test
