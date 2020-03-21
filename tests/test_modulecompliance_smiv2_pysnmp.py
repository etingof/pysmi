#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2020, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysmi/license.html
#
import sys
try:
    import unittest2 as unittest

except ImportError:
    import unittest

from pysmi.parser.smi import parserFactory
from pysmi.codegen.pysnmp import PySnmpCodeGen
from pysmi.codegen.symtable import SymtableCodeGen
from pysnmp.smi.builder import MibBuilder


class ModuleComplianceTestCase(unittest.TestCase):
    """
TEST-MIB DEFINITIONS ::= BEGIN
IMPORTS
  MODULE-COMPLIANCE
    FROM SNMPv2-CONF;

testCompliance MODULE-COMPLIANCE
 STATUS      current
 DESCRIPTION  "This is the MIB compliance statement"
 MODULE
  MANDATORY-GROUPS {
   testComplianceInfoGroup,
   testNotificationInfoGroup
  }
  GROUP     testNotificationGroup
  DESCRIPTION
        "Support for these notifications is optional."
  ::= { 1 3 }

END
 """

    def setUp(self):
        ast = parserFactory()().parse(self.__class__.__doc__)[0]
        mibInfo, symtable = SymtableCodeGen().genCode(ast, {}, genTexts=True)
        self.mibInfo, pycode = PySnmpCodeGen().genCode(ast, {mibInfo.name: symtable}, genTexts=True)
        codeobj = compile(pycode, 'test', 'exec')

        mibBuilder = MibBuilder()
        mibBuilder.loadTexts = True

        self.ctx = {'mibBuilder': mibBuilder}

        exec(codeobj, self.ctx, self.ctx)

    def testModuleComplianceSymbol(self):
        self.assertTrue(
            'testCompliance' in self.ctx,
            'symbol not present'
        )

    def testModuleComplianceName(self):
        self.assertEqual(
            self.ctx['testCompliance'].getName(),
            (1, 3),
            'bad name'
        )

    def testModuleComplianceDescription(self):
        self.assertEqual(
            self.ctx['testCompliance'].getDescription(),
            'This is the MIB compliance statement',
            'bad DESCRIPTION'
        )

    def testModuleComplianceClass(self):
        self.assertEqual(
            self.ctx['testCompliance'].__class__.__name__,
            'ModuleCompliance',
            'bad SYNTAX class'
        )

suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
