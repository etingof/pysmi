import os
import sys
import time
import imp
import struct
from pysmi.searcher.base import AbstractSearcher
from pysmi.compat import decode
from pysmi import debug
from pysmi import error

class PyFileSearcher(AbstractSearcher):
    suffixes = {}
    for sfx, mode, typ in imp.get_suffixes():
        if typ not in suffixes:
            suffixes[typ] = []
        suffixes[typ].append((sfx, mode))

    def __init__(self, path):
        self._path = os.path.normpath(decode(path))

    def __str__(self): return '%s{"%s"}' % (self.__class__.__name__, self._path)

    def fileExists(self, mibname, mtime, rebuild=False):
        if rebuild:
            debug.logger & debug.flagSearcher and debug.logger('pretend %s is very old' % mibname)
            return
        mibname = decode(mibname)
        pyfile = os.path.join(self._path, mibname)
        for format in imp.PY_COMPILED, imp.PY_SOURCE:
            for pySfx, pyMode in self.suffixes[format]:
                f = pyfile + pySfx
                if not os.path.exists(f) or not os.path.isfile(f):
                    debug.logger & debug.flagSearcher and debug.logger('%s not present or not a file' % f)
                    continue
                if format == imp.PY_COMPILED:
                    try:
                        pyData = open(f, pyMode).read(8)
                    except IOError:
                        raise error.PySmiSearcherError('failure opening compiled file %s: %s' % (f, sys.exc_info()[1]), searcher=self)
                    if pyData[:4] == imp.get_magic():
                        pyData = pyData[4:]
                        pyTime = struct.unpack('<L', pyData[:4])[0]
                        debug.logger & debug.flagSearcher and debug.logger('found %s, mtime %s' % (f, time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(pyTime))))
                        if pyTime >= mtime:
                            raise error.PySmiSourceNotModifiedError()
                        return
                    else:
                        debug.logger & debug.flagSearcher and debug.logger('bad magic in %s' % f)
                        continue
                else:
                    try:
                        pyTime = os.stat(f)[8]
                    except OSError:
                        raise error.PySmiSearcherError('failure opening compiled file %s: %s' % (f, sys.exc_info()[1]), searcher=self)

                    debug.logger & debug.flagSearcher and debug.logger('found %s, mtime %s' % (f, time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(pyTime))))
                    if pyTime >= mtime:
                        raise error.PySmiSourceNotModifiedError()

        raise error.PySmiCompiledFileNotFoundError('no compiled file %s found' % mibname, searcher=self)
