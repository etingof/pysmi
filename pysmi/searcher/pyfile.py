#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2019, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysmi/license.html
#
import os
import sys
import time
import struct
try:
    import importlib

    try:
        SOURCE_SUFFIXES = importlib.machinery.SOURCE_SUFFIXES
        BYTECODE_SUFFIXES = importlib.machinery.BYTECODE_SUFFIXES

    except Exception:
        raise ImportError()

except ImportError:
    import imp

    SOURCE_SUFFIXES = [s[0] for s in imp.get_suffixes()
                       if s[2] == imp.PY_SOURCE]
    BYTECODE_SUFFIXES = [s[0] for s in imp.get_suffixes()
                         if s[2] == imp.PY_COMPILED]

from pysmi.searcher.base import AbstractSearcher
from pysmi.compat import decode
from pysmi import debug
from pysmi import error


class PyFileSearcher(AbstractSearcher):
    """Figures out if given Python file (source or bytecode) exists at given
       location.
    """
    def __init__(self, path):
        """Create an instance of *PyFileSearcher* bound to specific directory.

           Args:
             path (str): path to local directory
        """
        self._path = os.path.normpath(decode(path))

    def __str__(self):
        return '%s{"%s"}' % (self.__class__.__name__, self._path)

    def fileExists(self, mibname, mtime, rebuild=False):
        if rebuild:
            debug.logger & debug.flagSearcher and debug.logger('pretend %s is very old' % mibname)
            return

        mibname = decode(mibname)
        pyfile = os.path.join(self._path, mibname)

        for pySfx in BYTECODE_SUFFIXES:
            f = pyfile + pySfx

            if not os.path.exists(f) or not os.path.isfile(f):
                debug.logger & debug.flagSearcher and debug.logger('%s not present or not a file' % f)
                continue

            try:
                fp = open(f, 'rb')
                pyData = fp.read(8)
                fp.close()

            except IOError:
                raise error.PySmiSearcherError('failure opening compiled file %s: %s' % (f, sys.exc_info()[1]),
                                               searcher=self)
            if pyData[:4] == imp.get_magic():
                pyData = pyData[4:]
                pyTime = struct.unpack('<L', pyData[:4])[0]
                debug.logger & debug.flagSearcher and debug.logger(
                    'found %s, mtime %s' % (f, time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(pyTime))))
                if pyTime >= mtime:
                    raise error.PySmiFileNotModifiedError()

                else:
                    raise error.PySmiFileNotFoundError('older file %s exists' % mibname, searcher=self)

            else:
                debug.logger & debug.flagSearcher and debug.logger('bad magic in %s' % f)
                continue

        for pySfx in SOURCE_SUFFIXES:
            f = pyfile + pySfx

            if not os.path.exists(f) or not os.path.isfile(f):
                debug.logger & debug.flagSearcher and debug.logger('%s not present or not a file' % f)
                continue

            try:
                pyTime = os.stat(f)[8]

            except OSError:
                raise error.PySmiSearcherError('failure opening compiled file %s: %s' % (f, sys.exc_info()[1]),
                                               searcher=self)

            debug.logger & debug.flagSearcher and debug.logger(
                'found %s, mtime %s' % (f, time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(pyTime))))

            if pyTime >= mtime:
                raise error.PySmiFileNotModifiedError()

        raise error.PySmiFileNotFoundError('no compiled file %s found' % mibname, searcher=self)
