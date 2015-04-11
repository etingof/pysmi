try:
    import unittest2 as unittest
except ImportError:
    import unittest
from pysmi.parser.smiv2 import SmiV2Parser
from pysmi.codegen.pysnmp import PySnmpCodeGen
from pysnmp.smi.builder import MibBuilder

class ModuleIdentityTestCase(unittest.TestCase):
    """
TEST-MIB DEFINITIONS ::= BEGIN
IMPORTS
 MODULE-IDENTITY
    FROM SNMPv2-SMI;

testModule MODULE-IDENTITY
 LAST-UPDATED "200001100000Z" -- Midnight 10 January 2000
 ORGANIZATION "AgentX Working Group"
 CONTACT-INFO "WG-email:   agentx@dorothy.bmc.com"
 DESCRIPTION  "This is the MIB module for the SNMP"
 REVISION     "200001100000Z" -- Midnight 10 January 2000
 DESCRIPTION  "Initial version published as RFC 2742."
 ::= { 1 3 }

END
 """

    def setUp(self):
        self.otherMibs, pycode = PySnmpCodeGen().genCode(SmiV2Parser().parse(self.__class__.__doc__))
        codeobj = compile(pycode, 'test', 'exec')

        mibBuilder = MibBuilder()
        mibBuilder.loadTexts = True

        self.ctx = { 'mibBuilder': mibBuilder }

        exec(codeobj, self.ctx, self.ctx)

    def testModuleIdentitySymbol(self):
        self.assertTrue(
            'testModule' in self.ctx,
            'symbol not present'
        )

    def testModuleIdentityName(self):
        self.assertEqual(
            self.ctx['testModule'].getName(),
            (1, 3),
            'bad name'
        )

    def testModuleIdentityLastUpdated(self):
        self.assertEqual(
            self.ctx['testModule'].getLastUpdated(),
            '200001100000Z',
            'bad LAST-UPDATED'
        )

    def testModuleIdentityOrganization(self):
        self.assertEqual(
            self.ctx['testModule'].getOrganization(),
            'AgentX Working Group',
            'bad ORGANIZATION'
        )

    def testModuleIdentityRevisions(self):
        self.assertTupleEqual(
            self.ctx['testModule'].getRevisions(),
            ('200001100000Z',),
            'bad REVISIONS'
        )

    def testModuleIdentityContactInfo(self):
        self.assertEqual(
            self.ctx['testModule'].getContactInfo(),
            'WG-email:   agentx@dorothy.bmc.com',
            'bad CONTACT-INFO'
        )

    def testModuleIdentityDescription(self):
        self.assertEqual(
            self.ctx['testModule'].getDescription(),
            'This is the MIB module for the SNMP',
            'bad DESCRIPTION'
        )

    def testModuleIdentityClass(self):
        self.assertEqual(
            self.ctx['testModule'].__class__.__name__,
            'ModuleIdentity',
            'bad SYNTAX class'
        )

if __name__ == '__main__': unittest.main()
