import sys
if sys.version_info[0:2] < (2, 7) or \
   sys.version_info[0:2] in ( (3, 0), (3, 1) ):
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
else:
    import unittest
from pysmi.parser.smiv2 import SmiV2Parser
from pysmi.codegen.pysnmp import PySnmpCodeGen
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
        self.otherMibs, pycode = PySnmpCodeGen().genCode(SmiV2Parser().parse(self.__class__.__doc__))
        codeobj = compile(pycode, 'test', 'exec')

        mibBuilder = MibBuilder()
        mibBuilder.loadTexts = True

        self.ctx = { 'mibBuilder': mibBuilder }

        exec(codeobj, self.ctx, self.ctx)

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
            'SmiV1',
            'bad SYNTAX class'
        )

if __name__ == '__main__': unittest.main()
