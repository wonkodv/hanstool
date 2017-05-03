#!/usr/bin/env python
"""Install ht3."""

from setuptools import setup, find_packages

setup(  name='ht3',
        version='0.2.0',
        description='Shell like Python interface',
        license='GPLv2',
        author='Wonko',
        author_email='wonko@hanstool.org',
        url='https://github.com/wonkodv/hanstool',
        packages=find_packages(),
        package_data={
            'ht3': [
                'default_scripts/*.py',
                'test_scripts/*.py',
            ]
        },
        entry_points={
            'console_scripts': [
                'ht=ht3.__main__'
            ]
        },
    )
