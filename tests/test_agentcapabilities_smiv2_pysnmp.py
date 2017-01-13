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
from pysmi.codegen.pysnmp import PySnmpCodeGen
from pysmi.codegen.symtable import SymtableCodeGen
from pysnmp.smi.builder import MibBuilder


class AgentCapabilitiesTestCase(unittest.TestCase):
    """
TEST-MIB DEFINITIONS ::= BEGIN
IMPORTS
    MODULE-IDENTITY
        FROM SNMPv2-SMI
    AGENT-CAPABILITIES
        FROM SNMPv2-CONF;

testCapability AGENT-CAPABILITIES
    PRODUCT-RELEASE "Test produce"
    STATUS          current
    DESCRIPTION
        "test capabilities"

    SUPPORTS        TEST-MIB
    INCLUDES        {
                        testSystemGroup,
                        testNotificationObjectGroup,
                        testNotificationGroup
                    }
    VARIATION       testSysLevelType
    ACCESS          read-only
    DESCRIPTION
        "Not supported."

    VARIATION       testSysLevelType
    ACCESS          read-only
    DESCRIPTION
        "Supported."

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

    def testAgentCapabilitiesSymbol(self):
        self.assertTrue(
            'testCapability' in self.ctx,
            'symbol not present'
        )

    def testAgentCapabilitiesName(self):
        self.assertEqual(
            self.ctx['testCapability'].getName(),
            (1, 3),
            'bad name'
        )

    def testAgentCapabilitiesDescription(self):
        self.assertEqual(
            self.ctx['testCapability'].getDescription(),
            'test capabilities',
            'bad DESCRIPTION'
        )

    # XXX SUPPORTS/INCLUDES/VARIATION/ACCESS not supported by pysnmp

    def testAgentCapabilitiesClass(self):
        self.assertEqual(
            self.ctx['testCapability'].__class__.__name__,
            'AgentCapabilities',
            'bad SYNTAX class'
        )


if __name__ == '__main__':
    unittest.main()
