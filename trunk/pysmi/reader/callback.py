import time
from pysmi.reader.base import AbstractReader
from pysmi.mibinfo import MibInfo
from pysmi import error
from pysmi import debug

class CallbackReader(AbstractReader):
    def __init__(self, cbFun, cbCtx=None):
        self._cbFun = cbFun
        self._cbCtx = cbCtx

    def __str__(self):
        return '%s{"%s"}' % (self.__class__.__name__, self._cbFun)

    def getData(self, timestamp, mibname):
        debug.logger & debug.flagReader and debug.logger('calling user callback %s for MIB %s that is newer than %s' % (self._cbFun, mibname, time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(timestamp))))
        res = self._cbFun(timestamp, mibname, self._cbCtx)
        if res:
            return MibInfo(mibfile=self._cbFun, mibname=mibname, alias=mibname), res
        raise error.PySmiSourceNotFoundError(mibnanme=mibname, reader=self)
