#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pysmi.sf.net/license.html
#
try:
    import unittest2 as unittest

except ImportError:
    import unittest

from pysmi.parser.smi import parserFactory
from pysmi.parser.dialect import smiV1Relaxed
from pysmi.codegen.pysnmp import PySnmpCodeGen
from pysmi.codegen.symtable import SymtableCodeGen
from pysnmp.smi.builder import MibBuilder


class SmiV1TestCase(unittest.TestCase):
    """
TEST-MIB DEFINITIONS ::= BEGIN

IMPORTS
    Counter, IpAddress, TimeTicks
        FROM RFC1155-SMI
    DisplayString, mib-2
        FROM RFC1213-MIB
    OBJECT-TYPE
        FROM RFC-1212

    NOTIFICATION-GROUP
        FROM SNMPv2-CONF;

testSmiV1 NOTIFICATION-GROUP
   NOTIFICATIONS    {
                        testStatusChangeNotify,
                        testClassEventNotify,
                        testThresholdBelowNotify
                    }
    STATUS          current
    DESCRIPTION
        "A collection of test notifications."
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

        exec (codeobj, self.ctx, self.ctx)

    def testSmiV1Symbol(self):
        self.assertTrue(
            'testSmiV1' in self.ctx,
            'symbol not present'
        )

    def testSmiV1Name(self):
        self.assertEqual(
            self.ctx['testSmiV1'].getName(),
            (1, 3),
            'bad name'
        )

    def testSmiV1Description(self):
        self.assertEqual(
            self.ctx['testSmiV1'].getDescription(),
            'A collection of test notifications.',
            'bad DESCRIPTION'
        )

    def testSmiV1Class(self):
        self.assertEqual(
            self.ctx['testSmiV1'].__class__.__name__,
            'NotificationGroup',
            'bad SYNTAX class'
        )


if __name__ == '__main__':
    unittest.main()
