
class AbstractCodeGen(object):
    def genCode(self, ast, symbolTable, **kwargs):
        raise NotImplementedError()
    
    def genIndex(self, mibsMap, **kwargs):
        raise NotImplementedError()

