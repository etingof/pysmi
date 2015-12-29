#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2016, Ilya Etingof <ilya@glas.net>
# License: http://pysmi.sf.net/license.html
#
import sys
if sys.version_info[0:2] < (2, 7) or \
   sys.version_info[0:2] in ( (3, 0), (3, 1) ):
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
else:
    import unittest
from pysmi.parser.smi import parserFactory
from pysmi.codegen.pysnmp import PySnmpCodeGen
from pysmi.codegen.symtable import SymtableCodeGen
from pysnmp.smi.builder import MibBuilder

class TrapTypeTestCase(unittest.TestCase):
    """
TEST-MIB DEFINITIONS ::= BEGIN
IMPORTS
  TRAP-TYPE
    FROM RFC-1215

  OBJECT-TYPE
    FROM RFC1155-SMI;

testId  OBJECT IDENTIFIER ::= { 1 3 }

testObject OBJECT-TYPE
    SYNTAX          INTEGER
    MAX-ACCESS      accessible-for-notify
    STATUS          current
    DESCRIPTION     "Test object"
 ::= { 1 3 }

testTrap     TRAP-TYPE
        ENTERPRISE  testId
        VARIABLES { testObject }
        DESCRIPTION
                "Test trap"
  ::= 1

END
 """

    def setUp(self):
        ast = parserFactory()().parse(self.__class__.__doc__)[0]
        mibInfo, symtable = SymtableCodeGen().genCode(ast, {}, genTexts=True)
        self.mibInfo, pycode = PySnmpCodeGen().genCode(ast, { mibInfo.name: symtable }, genTexts=True)
        codeobj = compile(pycode, 'test', 'exec')

        mibBuilder = MibBuilder()
        mibBuilder.loadTexts = True

        self.ctx = { 'mibBuilder': mibBuilder }

        exec(codeobj, self.ctx, self.ctx)

    def testTrapTypeSymbol(self):
        self.assertTrue(
            'testTrap' in self.ctx,
            'symbol not present'
        )

    def testTrapTypeName(self):
        self.assertEqual(
            self.ctx['testTrap'].getName(),
            (1, 3, 0, 1),
            'bad name'
        )

    def testTrapTypeDescription(self):
        self.assertEqual(
            self.ctx['testTrap'].getDescription(),
            'Test trap',
            'bad DESCRIPTION'
        )

    def testTrapTypeClass(self):
        self.assertEqual(
            self.ctx['testTrap'].__class__.__name__,
            'NotificationType',
            'bad SYNTAX class'
        )

if __name__ == '__main__': unittest.main()
