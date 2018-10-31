#!/usr/bin/env python
"""Install ht3-client"""

from setuptools import setup, find_packages

setup(  name='ht3-client',
        version='1.0',
        description='Client to ht3.daemon',
        license='GPLv2',
        author='Wonko',
        author_email='wonko@hanstool.org',
        url='https://github.com/wonkodv/ht3-client',
        packages=find_packages(),
        entry_points={
            'console_scripts': [
                'htc=ht3client.__main__'
            ]
        },
    )
