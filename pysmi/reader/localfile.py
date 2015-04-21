import os
import sys
import time
from pysmi.reader.base import AbstractReader
from pysmi import debug
from pysmi import error

class FileReader(AbstractReader):
    useIndexFile = True       # optional .index file mapping MIB to file name
    indexFile = '.index'
    def __init__(self, path, recursive=True, ignoreErrors=True):
        self._path = os.path.normpath(path)
        self._recursive = recursive
        self._ignoreErrors = ignoreErrors
        self._indexLoaded = False

    def __str__(self): return '%s{"%s"}' % (self.__class__.__name__, self._path)

    def getSubdirs(self, path, recursive=True, ignoreErrors=True):
        if not recursive:
            return [ path ]
        dirs = [ path ]
        try:
            subdirs = os.listdir(path)
        except OSError:
            if ignoreErrors:
                return dirs
            else:
                raise error.PySmiError('directory %s access error: %s' % (path, sys.exc_info()[1]))
        for d in subdirs:
            d = os.path.join(path, d)
            if os.path.isdir(d):
                dirs.extend(self.getSubdirs(d, recursive))
        return dirs

    def loadIndex(self, indexFile):
        mibIndex = {}
        if os.path.exists(indexFile):
            try:
                mibIndex = dict(
                    [x.split()[:2] for x in open(indexFile).readlines()]
                )
                debug.logger & debug.flagReader and debug.logger('built MIB index map from %s file, %s entries' % (indexFile, len(mibIndex)))
            except IOError:
                pass

        return mibIndex

    def getMibVariants(self, mibname):
        if self.useIndexFile:
            if not self._indexLoaded:
                self._mibIndex = self.loadIndex(
                    os.path.join(self._path, self.indexFile)
                )
                self._indexLoaded = True

            if mibname in self._mibIndex:
                debug.logger & debug.flagReader and debug.logger('found %s in MIB index: %s' % (mibname, self._mibIndex[mibname]))
                return [ self._mibIndex[mibname] ]

        return super(FileReader, self).getMibVariants(mibname)

    def getData(self, timestamp, mibname):
        debug.logger & debug.flagReader and debug.logger('%slooking for MIB %s that is newer than %s' % (self._recursive and 'recursively ' or '', mibname, time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(timestamp))))
        for path in self.getSubdirs(self._path, self._recursive,
                                    self._ignoreErrors):
            for mibfile in self.getMibVariants(mibname):
                f = os.path.join(path, mibfile)
                debug.logger & debug.flagReader and debug.logger('trying MIB %s' % f)
                if os.path.exists(f) and os.path.isfile(f):
                    try:
                        lastModified = os.stat(f)[8]
                        if lastModified > timestamp:
                            debug.logger & debug.flagReader and debug.logger('source MIB %s is new enough (%s), fetching data...' % (f, time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(lastModified))))
                            return open(f, mode='rb').read(self.maxMibSize).decode('utf-8', 'ignore')
                    except (OSError, IOError):
                        debug.logger & debug.flagReader and debug.logger('source file %s open failure: %s' % (f, sys.exc_info()[1]))
                        if not self._ignoreErrors:
                            raise error.PySmiError('file %s access error: %s' % (f, sys.exc_info()[1]))

                    raise error.PySmiSourceNotModifiedError('source MIB %s is older than needed' % f, reader=self)

        raise error.PySmiSourceNotFoundError('source MIB %s not found' % mibname, reader=self)

if __name__ == '__main__':
    debug.setLogger(debug.Debug('all'))

    f = FileReader('/usr/share/snmp/mibs')
    print(f.getData(10000,  'SNMPv2-SMI'))
    print(f.getData(10000,  'SNMPv2-SMI2'))
