"""Fills the initial environment."""
import os
import time
import os.path

import ht3
from . import Env
from ht3.check import CHECK
import ht3.check
import ht3.complete
import ht3.command


def import_element( mod, name):
    """add the element ``name`` from module ``mod``"""
    Env.dict[name] = getattr(mod, name)

Env.__ = []
Env._  = None

Env['ht3'] = ht3

for k, v in os.environ.items():
    if k[:4] == 'HT3_':
        Env[k[4:]] = v



import_element(ht3.check, 'CHECK')

import_element(ht3.complete, 'complete_all')
import_element(ht3.complete, 'complete_py')
import_element(ht3.complete, 'complete_command')
import_element(ht3.complete, 'filter_completions')

import_element(ht3.command, 'cmd');
import_element(ht3.command, 'COMMANDS');
import_element(ht3.command, 'run_command');

import_element(ht3.lib, 'evaluate_py_expression');
import_element(ht3.lib, 'execute_py_expression');
import_element(ht3.lib, 'start_thread');

import_element(time, 'sleep')
import_element(os.path, 'expanduser')

if CHECK.os.windows:
    __import__('ht3.env.windows')

__import__('ht3.env.log')
__import__('ht3.env.handler')
__import__('ht3.env.fake_input')
__import__('ht3.env.process')
__import__('ht3.env.helpers')


