
class MibInfo(object):
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])

class AbstractCodeGen(object):
    def genCode(self, ast, **kwargs):
        raise NotImplementedError()
    
    def genIndex(self, mibsMap, **kwargs):
        raise NotImplementedError()

