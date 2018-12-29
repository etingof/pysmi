#!/usr/bin/env python
#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2019, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysmi/license.html
#
"""SNMP SMI/MIB Parser

A pure-Python implementation of SNMP/SMI MIB parsing and
conversion library.
"""

import os
import sys

classifiers = """\
Development Status :: 5 - Production/Stable
Environment :: Console
Intended Audience :: Developers
Intended Audience :: Education
Intended Audience :: Information Technology
Intended Audience :: System Administrators
Intended Audience :: Telecommunications Industry
License :: OSI Approved :: BSD License
Natural Language :: English
Operating System :: OS Independent
Programming Language :: Python :: 2
Programming Language :: Python :: 2.4
Programming Language :: Python :: 2.5
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.2
Programming Language :: Python :: 3.3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Topic :: Communications
Topic :: System :: Monitoring
Topic :: System :: Networking :: Monitoring
Topic :: Software Development :: Libraries :: Python Modules
"""


def howto_install_setuptools():
    print("""
   Error: You need setuptools Python package!

   It's very easy to install it, just type:

   wget https://bootstrap.pypa.io/ez_setup.py
   python ez_setup.py

   Then you could make eggs from this package.
""")


if sys.version_info[:2] < (2, 4):
    print("ERROR: this package requires Python 2.4 or later!")
    sys.exit(1)


try:
    from setuptools import setup, Command

    params = {'zip_safe': True}

except ImportError:
    for arg in sys.argv:
        if 'egg' in arg:
            howto_install_setuptools()
            sys.exit(1)

    from distutils.core import setup, Command

    params = {}

    if sys.version_info[:2] < (2, 6):
        params['requires'] = ['ply(==3.4)', 'simplejson(==2.1)']
    else:
        params['requires'] = ['ply']

    if sys.version_info[:2] < (2, 7):
        params['requires'].append('ordereddict')
else:
    if sys.version_info[:2] < (2, 6):
        params['install_requires'] = ['ply==3.4', 'simplejson==2.1']
    else:
        params['install_requires'] = ['ply']

    if sys.version_info[:2] < (2, 7):
        params['install_requires'].append('ordereddict')

doclines = [x.strip() for x in (__doc__ or '').split('\n') if x]

params.update({
    'name': 'pysmi',
    'version': open(os.path.join('pysmi', '__init__.py')).read().split('\'')[1],
    'description': doclines[0],
    'long_description': ' '.join(doclines[1:]),
    'maintainer': 'Ilya Etingof <etingof@gmail.com>',
    'author': 'Ilya Etingof',
    'author_email': 'etingof@gmail.com',
    'url': 'https://github.com/etingof/pysmi',
    'platforms': ['any'],
    'classifiers': [x for x in classifiers.split('\n') if x],
    'license': 'BSD',
    'packages': ['pysmi',
                 'pysmi.reader',
                 'pysmi.searcher',
                 'pysmi.lexer',
                 'pysmi.parser',
                 'pysmi.codegen',
                 'pysmi.borrower',
                 'pysmi.writer'],
    'scripts': [os.path.join('scripts', 'mibdump.py'),
                os.path.join('scripts', 'mibcopy.py')]
})

# handle unittest discovery feature
if sys.version_info[0:2] < (2, 7) or \
                sys.version_info[0:2] in ((3, 0), (3, 1)):
    try:
        import unittest2 as unittest
    except ImportError:
        unittest = None
else:
    import unittest

if unittest:
    class PyTest(Command):
        user_options = []

        def initialize_options(self): pass

        def finalize_options(self): pass

        def run(self):
            suite = unittest.defaultTestLoader.discover('tests')
            unittest.TextTestRunner(verbosity=2).run(suite)


    params['cmdclass'] = {'test': PyTest}

setup(**params)
