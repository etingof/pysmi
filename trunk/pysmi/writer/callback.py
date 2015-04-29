import sys
from pysmi.writer.base import AbstractWriter
from pysmi import debug
from pysmi import error

class CallbackWriter(AbstractWriter):
    def __init__(self, cbFun, cbCtx=None):
        self._cbFun = cbFun
        self._cbCtx = cbCtx

    def __str__(self):
        return '%s{"%s"}' % (self.__class__.__name__, self._cbFun)

    def putData(self, mibname, data, dryRun=False):
        if dryRun:
            debug.logger & debug.flagWriter and debug.logger('dry run mode')
            return

        try:
            self._cbFun(mibname, data, self._cbCtx)
        except Exception:
            raise error.PySmiWriterError('user callback %s failure writing %s: %s' % (self._cbFun, mibname, sys.exc_info()[1]), writer=self)

        debug.logger & debug.flagWriter and debug.logger('user callback for %s succeeded' % mibname)

if __name__ == '__main__':
    from pysmi import debug

    debug.setLogger(debug.Debug('all'))

    f = CallbackWriter(lambda m,d,a,c: sys.stdout.write(d))

    f.putData('X', 'print(123)\n')
