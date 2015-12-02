import unittest

class TestIntegration(unittest.TestCase):
    from ht3.lib import load_scripts
    from ht3.command import run_command
    from ht3.env import Env
    from ht3.env import initial

    load_scripts('test_scripts')
    assert run_command('test') == 'Integration Tests ran'
