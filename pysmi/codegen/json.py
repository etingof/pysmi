#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2016, Ilya Etingof <ilya@glas.net>
# License: http://pysmi.sf.net/license.html
#
from pysmi.mibinfo import MibInfo
from pysmi.codegen.base import AbstractCodeGen
from pysmi import debug


class JsonCodeGen(AbstractCodeGen):
    """Json code generation backend.

       Dumps MIB files into JSON documents.
    """

    def genCode(self, ast, symbolTable, **kwargs):
        debug.logger & debug.flagCodegen and debug.logger('%s invoked' % self.__class__.__name__)
        return MibInfo(oid=None, name='', imported=[]), ''

    def genIndex(self, mibsMap, **kwargs):
        return ''
