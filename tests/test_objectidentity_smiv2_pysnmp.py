#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2019, Ilya Etingof <etingof@gmail.com>
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


class ObjectIdentityTestCase(unittest.TestCase):
    """
TEST-MIB DEFINITIONS ::= BEGIN
IMPORTS
    OBJECT-IDENTITY
FROM SNMPv2-SMI;

testObject OBJECT-IDENTITY
    STATUS          current
    DESCRIPTION     "Initial version"
    REFERENCE       "ABC"

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

    def testObjectIdentitySymbol(self):
        self.assertTrue(
            'testObject' in self.ctx,
            'symbol not present'
        )

    def testObjectIdentityName(self):
        self.assertEqual(
            self.ctx['testObject'].getName(),
            (1, 3),
            'bad name'
        )

    def testObjectIdentityDescription(self):
        self.assertEqual(
            self.ctx['testObject'].getDescription(),
            'Initial version\n',
            'bad DESCRIPTION'
        )

    def testObjectIdentityReference(self):
        self.assertEqual(
            self.ctx['testObject'].getReference(),
            'ABC',
            'bad REFERENCE'
        )

    def testObjectIdentityClass(self):
        self.assertEqual(
            self.ctx['testObject'].__class__.__name__,
            'ObjectIdentity',
            'bad SYNTAX class'
        )


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)
