class AbstractSearcher(object):
    def getTimestamp(self, mibname, rebuild=False):
        raise NotImplementedError()
