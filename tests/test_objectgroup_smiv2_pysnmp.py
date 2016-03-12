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
from pysmi.parser.dialect import smiV2
from pysmi.codegen.pysnmp import PySnmpCodeGen
from pysmi.codegen.symtable import SymtableCodeGen
from pysnmp.smi.builder import MibBuilder

class ObjectGroupTestCase(unittest.TestCase):
    """
TEST-MIB DEFINITIONS ::= BEGIN
IMPORTS
  OBJECT-GROUP
    FROM SNMPv2-CONF;

testObjectGroup OBJECT-GROUP
    OBJECTS         {
                        testStorageType,
                        testRowStatus
                    }
    STATUS          current
    DESCRIPTION
        "A collection of test objects."
 ::= { 1 3 }

END
 """

    def setUp(self):
        ast = parserFactory(**smiV2)().parse(self.__class__.__doc__)[0]
        mibInfo, symtable = SymtableCodeGen().genCode(ast, {}, genTexts=True)
        self.mibInfo, pycode = PySnmpCodeGen().genCode(ast, { mibInfo.name: symtable }, genTexts=True)
        codeobj = compile(pycode, 'test', 'exec')

        mibBuilder = MibBuilder()
        mibBuilder.loadTexts = True

        self.ctx = { 'mibBuilder': mibBuilder }

        exec(codeobj, self.ctx, self.ctx)

    def testObjectGroupSymbol(self):
        self.assertTrue(
            'testObjectGroup' in self.ctx,
            'symbol not present'
        )

    def testObjectGroupName(self):
        self.assertEqual(
            self.ctx['testObjectGroup'].getName(),
            (1, 3),
            'bad name'
        )

    def testObjectGroupDescription(self):
        self.assertEqual(
            self.ctx['testObjectGroup'].getDescription(),
            'A collection of test objects.',
            'bad DESCRIPTION'
        )

    def testObjectGroupObjects(self):
        self.assertTupleEqual(
            self.ctx['testObjectGroup'].getObjects(),
            (('TEST-MIB', 'testStorageType'), ('TEST-MIB', 'testRowStatus')),
            'bad OBJECTS'
        )

    def testObjectGroupClass(self):
        self.assertEqual(
            self.ctx['testObjectGroup'].__class__.__name__,
            'ObjectGroup',
            'bad SYNTAX class'
        )

if __name__ == '__main__':
    unittest.main()
