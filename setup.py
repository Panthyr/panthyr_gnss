# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

setup(
    name='p_gnss',
    version='v1.0.0',
    packages=find_packages(exclude='old'),
    entry_points={
        'console_scripts': ['test_gnss = panthyr_gnss.test_gnss:test_gnss'],
    },
)
