class AbstractSearcher(object):
    def fileExists(self, mibname, mtime, rebuild=False):
        raise NotImplementedError()
