class AbstractWriter(object):
    def putData(self, mibname, data, comments=[], dryRun=False):
        raise NotImplementedError()
