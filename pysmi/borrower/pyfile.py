#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2019, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysmi/license.html
#
try:
    import importlib

    SOURCE_SUFFIXES = importlib.machinery.SOURCE_SUFFIXES

except ImportError:
    import imp

    SOURCE_SUFFIXES = [imp.PY_SOURCE]

from pysmi.borrower.base import AbstractBorrower


class PyFileBorrower(AbstractBorrower):
    """Create PySNMP MIB file borrowing object"""
    exts = SOURCE_SUFFIXES
