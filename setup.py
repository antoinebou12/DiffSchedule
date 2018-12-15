#!/usr/bin/env python

import runpy
from setuptools import setup, find_packages

LONG_DESCRIPTION = open('README.md').read()

ns_version = runpy.run_path('version.py')

console_scripts = ['']

extras_require = {}

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

SETUP = dict(
    name='Freetime',
    version=ns_version['__version__'],
    description='Compare multiple calender for free time in both calender',
    long_description=LONG_DESCRIPTION,
    url='',
    license='MIT',
    author='Antoine Boucher',
    author_email='',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={'console_scripts': console_scripts},
    extras_require=extras_require
)

if __name__ == '__main__':
    setup(**SETUP)
