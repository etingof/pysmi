class AbstractWriter(object):
    def putData(self, mibname, data, alias=None, dryRun=False):
        raise NotImplementedError()
