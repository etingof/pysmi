import time
from pysmi.reader.base import AbstractReader
from pysmi import debug

class CallbackReader(AbstractReader):
    def __init__(self, cbfun, cbctx=None):
        self._cbfun = cbfun
        self._cbctx = cbctx

    def __str__(self):
        return '%s{"%s"}' % (self.__class__.__name__, self._cbfun)

    def getData(self, timestamp, mibname):
        debug.logger & debug.flagReader and debug.logger('calling user callback %s for MIB %s that is newer than %s' % (self._cbfun, mibname, time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(timestamp))))
        return self._cbfun(timestamp, mibname, self._cbctx)

if __name__ == '__main__':
    debug.setLogger(debug.Debug('all'))

    def usercbfun(timestamp, mibname, cbctx):
        return 'MIB %s text' % mibname

    f = CallbackReader(usercbfun)

    print(f.getData(10000,  'SNMPv2-SMI'))
    print(f.getData(10000,  'SNMPv2-SMI2'))
