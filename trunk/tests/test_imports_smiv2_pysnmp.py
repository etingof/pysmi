try:
    import unittest2 as unittest
except ImportError:
    import unittest
from pysmi.parser.smiv2 import SmiV2Parser
from pysmi.codegen.pysnmp import PySnmpCodeGen
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
        self.otherMibs, pycode = PySnmpCodeGen().genCode(SmiV2Parser().parse(self.__class__.__doc__))
        codeobj = compile(pycode, 'test', 'exec')

        self.ctx = { 'mibBuilder': MibBuilder() }

        exec(codeobj, self.ctx, self.ctx)

    def testModuleImportsRequiredMibs(self):
        self.assertTupleEqual(
            self.otherMibs,
            ('ASN1', 'ASN1-ENUMERATION', 'ASN1-REFINEMENT',
             'SNMP-FRAMEWORK-MIB', 'SNMPv2-SMI'),
            'imported MIBs not reported'
        )

    def testModuleCheckImportedSymbol(self):
        self.assertTrue(
            'SnmpAdminString' in self.ctx,
            'imported symbol not present'
        )

if __name__ == '__main__': unittest.main()
