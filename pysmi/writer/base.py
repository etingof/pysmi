class AbstractWriter(object):
    def putData(self, mibname, data, dryRun=False):
        raise NotImplementedError()
