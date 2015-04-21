import os
from pysmi import debug

class AbstractReader(object):
    maxMibSize = 10000000     # MIBs can't be that large
    useIndexFile = True       # optional .index file mapping MIB to file name
    indexFile = '.index'
    fuzzyMatching = True      # try different file names while searching for MIB
    exts = ['',
            os.path.extsep + 'txt',
            os.path.extsep + 'mib',
            os.path.extsep + 'my']
    exts.extend([ x.upper() for x in exts if x ])

    def __init__(self):
        self._indexFileAge = 0

    def setOptions(self, **kwargs):
        self.fuzzyMatching = kwargs.get('fuzzyMatching', self.fuzzyMatching)
        return self

    def getMibVariants(self, mibname, path=None):
        if self.useIndexFile and path != None:
            indexFile = os.path.join(path, self.indexFile)
            if os.path.exists(indexFile):
                try:
                    mtime = os.stat(indexFile)
                except OSError:
                    mtime = -1
                    self._mibMap = {}
                if mtime > 0 and mtime != self._indexFileAge:
                    try:
                        self._mibMap = dict(
                            [x.split(' ', 1) for x in open(indexFile).readlines()]
                        )
                        self._indexFileAge = mtime
                        debug.logger & debug.flagReader and debug.logger('built MIB index map from %s file, mtime %s, %s entries' % (indexFile, mtime, len(self._mibMap)))

                    except IOError:
                        pass

                if mibname in self._mibMap:
                    debug.logger & debug.flagReader and debug.logger('found %s in MIB index: %s' % (mibname, self._mibMap[mibname]))
                    return [ self._mibMap[mibname] ]

        filenames = [ mibname, mibname.upper(), mibname.lower() ]
        if self.fuzzyMatching:
            part = filenames[-1].find('-mib')
            if part != -1:
                filenames.extend(
                    [ x[:part] for x in filenames ]
                )
            else:
                suffixed = mibname + '-mib'
                filenames.append(suffixed.upper())
                filenames.append(suffixed.lower())

        return (x+y for x in filenames for y in self.exts)

    def getData(self, timestamp, filename):
        raise NotImplementedError()
