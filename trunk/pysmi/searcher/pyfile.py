import os
import sys
import time
import imp
import struct
from pysmi.searcher.base import AbstractSearcher
from pysmi import debug
from pysmi import error

class PyFileSearcher(AbstractSearcher):
    suffixes = {}
    for sfx, mode, typ in imp.get_suffixes():
        if typ not in suffixes:
            suffixes[typ] = []
        suffixes[typ].append((sfx, mode))

    def __init__(self, path):
        self._path = os.path.normpath(path)

    def __str__(self): return '%s{"%s"}' % (self.__class__.__name__, self._path)

    def getTimestamp(self, mibname, rebuild=False):
        if rebuild:
            debug.logger & debug.flagSearcher and debug.logger('pretend %s is very old' % mibname)
            return 0  # beginning of time
        pyfile = os.path.join(self._path, mibname.upper())
        for format in imp.PY_COMPILED, imp.PY_SOURCE:
            for pySfx, pyMode in self.suffixes[format]:
                f = pyfile + pySfx
                if not os.path.exists(f):
                    continue
                if format == imp.PY_COMPILED:
                    try:
                        pyData = open(f, pyMode).read(8)
                    except IOError:
                        raise error.PySmiError('failure opening compiled file %s: %s' % (f, sys.exc_info()[1]))
                    if pyData[:4] == imp.get_magic():
                        pyData = pyData[4:]
                        pyTime = struct.unpack('<L', pyData[:4])[0]
                        debug.logger & debug.flagSearcher and debug.logger('found %s, mtime %s' % (f, time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(pyTime))))
                        return pyTime
                    else:
                        debug.logger & debug.flagSearcher and debug.logger('bad magic in %s' % f)
                        continue
                else:
                    try:
                        pyTime = os.stat(f)[8]
                    except OSError:
                        raise error.PySmiError('failure opening compiled file %s: %s' % (f, sys.exc_info()[1]))

                    debug.logger & debug.flagSearcher and debug.logger('found %s, mtime %s' % (f, time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(pyTime))))
                    return pyTime

        debug.logger & debug.flagSearcher and debug.logger('no compiled file %s found' % mibname)

        raise error.PySmiSourceNotFound(mibname)

if __name__ == '__main__':
    from pysmi import debug

    debug.setLogger(debug.Debug('all'))

    f = PyFileSearcher('/tmp/x')

    f.getTimestamp('X')
