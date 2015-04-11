import os

class AbstractReader(object):
    maxMibSize = 10000000   # MIBs can't be that large
    exts = ('',
            os.path.extsep + 'txt',
            os.path.extsep + 'mib',
            os.path.extsep + 'my')
    def getData(self, timestamp, filename):
        raise NotImplementedError()
