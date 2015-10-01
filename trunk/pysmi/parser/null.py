from pysmi.parser.base import AbstractParser

class NullParser(AbstractParser):
    def __init__(self, startSym='mibFile', tempdir=''):
        pass

    def reset(self):
        pass

    def parse(self, data, **kwargs):
        return []
