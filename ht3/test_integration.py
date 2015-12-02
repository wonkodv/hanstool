import unittest
import pkg_resources

class TestIntegration(unittest.TestCase):
    from ht3.lib import load_scripts
    from ht3.command import run_command
    from ht3.env import Env
    from ht3.env import initial

    load_scripts(pkg_resources.resource_filename(__name__,'test_scripts'))
    assert run_command('test') == 'Integration Tests ran'
