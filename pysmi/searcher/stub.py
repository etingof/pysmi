import time
from pysmi.searcher.base import AbstractSearcher
from pysmi import debug
from pysmi import error

class StubSearcher(AbstractSearcher):
    def __init__(self, *mibnames):
        self._mibnames = mibnames

    def __str__(self): return '%s' % self.__class__.__name__

    def getTimestamp(self, mibname, rebuild=False):
        if mibname in self._mibnames:
            debug.logger & debug.flagSearcher and debug.logger('pretend compiled %s exists and is very new' % mibname)
            raise error.PySmiCompiledFileTakesPrecedenceError('compiled file %s is among %s' % (mibname, ', '.join(self._mibnames)), searcher=self)

        raise error.PySmiCompiledFileNotFoundError('no compiled file %s found among %s' % (mibname, ', '.join(self._mibnames)), searcher=self)

if __name__ == '__main__':
    from pysmi import debug

    debug.setLogger(debug.Debug('all'))

    f = StubSearcher('X')

    print(f.getTimestamp('X'))
    print(f.getTimestamp('Y'))
