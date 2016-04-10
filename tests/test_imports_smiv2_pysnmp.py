#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2016, Ilya Etingof <ilya@glas.net>
# License: http://pysmi.sf.net/license.html
#
try:
    import unittest2 as unittest

except ImportError:
    import unittest

from pysmi.parser.smi import parserFactory
from pysmi.codegen.pysnmp import PySnmpCodeGen
from pysmi.codegen.symtable import SymtableCodeGen
from pysnmp.smi.builder import MibBuilder


class ImportClauseTestCase(unittest.TestCase):
    """
TEST-MIB DEFINITIONS ::= BEGIN
IMPORTS
 MODULE-IDENTITY, OBJECT-TYPE, Unsigned32, mib-2
    FROM SNMPv2-SMI
 SnmpAdminString
    FROM SNMP-FRAMEWORK-MIB;


END
 """

    def setUp(self):
        ast = parserFactory()().parse(self.__class__.__doc__)[0]
        mibInfo, symtable = SymtableCodeGen().genCode(ast, {}, genTexts=True)
        self.mibInfo, pycode = PySnmpCodeGen().genCode(ast, {mibInfo.name: symtable}, genTexts=True)
        codeobj = compile(pycode, 'test', 'exec')

        self.ctx = {'mibBuilder': MibBuilder()}

        exec (codeobj, self.ctx, self.ctx)

    def testModuleImportsRequiredMibs(self):
        self.assertTupleEqual(
            self.mibInfo.imported,
            ('SNMP-FRAMEWORK-MIB', 'SNMPv2-CONF', 'SNMPv2-SMI', 'SNMPv2-TC'),
            'imported MIBs not reported'
        )

    def testModuleCheckImportedSymbol(self):
        self.assertTrue(
            'SnmpAdminString' in self.ctx,
            'imported symbol not present'
        )


if __name__ == '__main__':
    unittest.main()
