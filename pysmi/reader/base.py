import os
from pysmi import debug

class AbstractReader(object):
    maxMibSize = 10000000     # MIBs can't be that large
    fuzzyMatching = True      # try different file names while searching for MIB
    exts = ['',
            os.path.extsep + 'txt',
            os.path.extsep + 'mib',
            os.path.extsep + 'my']
    exts.extend([ x.upper() for x in exts if x ])

    def setOptions(self, **kwargs):
        self.fuzzyMatching = kwargs.get('fuzzyMatching', self.fuzzyMatching)
        return self

    def getMibVariants(self, mibname):
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
