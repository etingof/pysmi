from pysmi import error
from pysmi import debug

class AbstractBorrower(object):
    genTexts = False
    exts = []

    def __init__(self, reader, genTexts=None):
        self._reader = reader.setOptions(exts=self.exts)
        if genTexts is not None:
            self.genTexts = genTexts

    def __str__(self): return '%s{%s, genTexts=%s}' % (self.__class__.__name__, self._reader, self.genTexts)

    def setOptions(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])
        return self

    def getData(self, mibname, **kwargs):
        if bool(kwargs.get('genTexts')) != self.genTexts:
            debug.logger & debug.flagBorrower and debug.logger('skipping incompatible borrower %s for file %s' % (self, mibname))
            raise error.PySmiFileNotFoundError(mibname=mibname, reader=self._reader)

        debug.logger & debug.flagBorrower and debug.logger('trying to borrow file %s from %s' % (mibname, self._reader))
        return self._reader.getData(mibname)
