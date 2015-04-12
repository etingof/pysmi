import os

class AbstractReader(object):
    maxMibSize = 10000000   # MIBs can't be that large
    fuzzyMatching = True      # try different file names while searching for MIB
    exts = ('',
            os.path.extsep + 'txt',
            os.path.extsep + 'mib',
            os.path.extsep + 'my')

    def setOptions(self, **kwargs):
        self.fuzzyMatching = kwargs.get('fuzzyMatching', self.fuzzyMatching)
        return self

    def getMibVariants(self, filename):
        filenames = [ filename, filename.upper(), filename.lower() ]
        if self.fuzzyMatching:
            part = filenames[-1].find('-mib')
            if part != -1:
                filenames.extend(
                    [ x[:part] for x in filenames ]
                )
            else:
                suffixed = filename + '-mib'
                filenames.append(suffixed.upper())
                filenames.append(suffixed.lower())

        return (x+y for x in filenames for y in self.exts)

    def getData(self, timestamp, filename):
        raise NotImplementedError()
