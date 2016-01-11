import unittest
import pkg_resources

class TestIntegration(unittest.TestCase):
    from ht3.scripts import load_scripts
    from ht3.command import run_command

    load_scripts(pkg_resources.resource_filename(__name__,'test_scripts'))
    assert run_command('test silent') == 'Integration Tests ran'
