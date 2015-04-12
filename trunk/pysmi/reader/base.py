import os

class AbstractReader(object):
    maxMibSize = 10000000   # MIBs can't be that large
    exts = ('',
            os.path.extsep + 'txt',
            os.path.extsep + 'mib',
            os.path.extsep + 'my')
    def getMibVariants(self, filename):
        filenames = [ filename, filename.upper(), filename.lower() ]
        if filenames[-1][-4:] == '-mib': 
            filenames.append(filenames[-1][:-4])
            filenames.append(filenames[-1].upper())

        return (x+y for x in filenames for y in self.exts)

    def getData(self, timestamp, filename):
        raise NotImplementedError()
