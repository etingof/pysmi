import os
import sys
import time
from pysmi.reader.base import AbstractReader
from pysmi import debug
from pysmi import error

class FileReader(AbstractReader):
    def __init__(self, path, recursive=True):
        self._path = os.path.normpath(path)
        self._recursive = recursive

    def __str__(self): return '%s{"%s"}' % (self.__class__.__name__, self._path)

    def getSubdirs(self, path, recursive):
        if not recursive:
            return [ path ]
        dirs = [ path ]
        for d in os.listdir(path):
            d = os.path.join(path, d)
            if os.path.isdir(d):
                dirs.extend(self.getSubdirs(d, recursive))
        return dirs

    def getData(self, timestamp, mibname):
        debug.logger & debug.flagReader and debug.logger('%slooking for MIB %s that is newer than %s' % (self._recursive and 'recursively ' or '', mibname, time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(timestamp))))
        for path in self.getSubdirs(self._path, self._recursive):
            for mibfile in self.getMibVariants(mibname):
                f = os.path.join(path, mibfile)
                debug.logger & debug.flagReader and debug.logger('trying MIB %s' % f)
                if os.path.exists(f):
                    try:
                        lastModified = os.stat(f)[8]
                        if lastModified > timestamp:
                            debug.logger & debug.flagReader and debug.logger('source MIB %s is new enough (%s), fetching data...' % (f, time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(lastModified))))
                            return open(f, mode='rb').read(self.maxMibSize).decode('utf-8', 'ignore')
                    except (OSError, IOError):
                        debug.logger & debug.flagReader and debug.logger('source file %s open failure: %s' % (f, sys.exc_info()[1]))

                    raise error.PySmiSourceNotModifiedError('source MIB %s is older than needed' % f, reader=self)

        raise error.PySmiSourceNotFoundError('source MIB %s not found' % mibname, reader=self)

if __name__ == '__main__':
    debug.setLogger(debug.Debug('all'))

    f = FileReader('/usr/share/snmp/mibs')
    print(f.getData(10000,  'SNMPv2-SMI'))
    print(f.getData(10000,  'SNMPv2-SMI2'))
