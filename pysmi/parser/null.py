import os
import sys
from pysmi.parser.base import AbstractParser
from pysmi import error
from pysmi import debug

class NullParser(AbstractParser):
    def __init__(self, startSym='mibFile', tempdir=''):
        pass

    def reset(self):
        pass

    def parse(self, data, **kwargs):
        return []
