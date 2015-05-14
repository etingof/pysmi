class AbstractWriter(object):
    def setOptions(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])
        return self

    def putData(self, mibname, data, comments=[], dryRun=False):
        raise NotImplementedError()
