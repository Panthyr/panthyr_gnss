# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

setup(
    name='p_gnss',
    version='0.1.0-beta',
    packages=find_packages(exclude='old'),
    entry_points={
        'console_scripts':
        ['test_gnss = test_gnss.test_gnss'],
    },
)
