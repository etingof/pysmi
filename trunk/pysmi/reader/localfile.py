import os
import sys
import time
from pysmi.reader.base import AbstractReader
from pysmi import debug
from pysmi import error

class FileReader(AbstractReader):
    def __init__(self, path):
        self._path = os.path.normpath(path)

    def __str__(self): return '%s{"%s"}' % (self.__class__.__name__, self._path)

    def getData(self, timestamp, mibname):
        debug.logger & debug.flagReader and debug.logger('looking for MIB %s that is newer than %s' % (mibname, time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(timestamp))))
        for ext in self.exts:
            for mibfile in mibname, mibname.upper(), mibname.lower():
                f = os.path.join(self._path, mibfile+ext)
                if os.path.exists(f):
                    debug.logger & debug.flagReader and debug.logger('trying MIB %s' % f)
                    try:
                        lastModified = os.stat(f)[8]
                        if lastModified > timestamp:
                            debug.logger & debug.flagReader and debug.logger('source MIB %s is new enough (%s), fetching data...' % (f, time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(lastModified))))
                            return open(f, mode='rb').read(self.maxMibSize).decode('utf-8', 'ignore')
                    except (OSError, IOError):
                        debug.logger & debug.flagReader and debug.logger('source file %s open failure: %s' % (f, sys.exc_info()[1]))

                    debug.logger & debug.flagReader and debug.logger('source MIB %s is older than needed' % f)
                    raise error.PySmiSourceNotModified(mibname, timestamp)

        debug.logger & debug.flagReader and debug.logger('source MIB %s not found' % mibname)
        raise error.PySmiSourceNotFound(mibname, timestamp)

if __name__ == '__main__':
    debug.setLogger(debug.Debug('all'))

    f = FileReader('/usr/share/snmp/mibs')
    print(f.getData(10000,  'SNMPv2-SMI'))
    print(f.getData(10000,  'SNMPv2-SMI2'))
