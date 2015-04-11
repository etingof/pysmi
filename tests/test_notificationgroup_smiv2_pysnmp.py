try:
    import unittest2 as unittest
except ImportError:
    import unittest
from pysmi.parser.smiv2 import SmiV2Parser
from pysmi.codegen.pysnmp import PySnmpCodeGen
from pysnmp.smi.builder import MibBuilder

class NotificationGroupTestCase(unittest.TestCase):
    """
TEST-MIB DEFINITIONS ::= BEGIN
IMPORTS
  NOTIFICATION-GROUP
    FROM SNMPv2-CONF;

testNotificationGroup NOTIFICATION-GROUP
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

    def testNotificationGroupSymbol(self):
        self.assertTrue(
            'testNotificationGroup' in self.ctx,
            'symbol not present'
        )

    def testNotificationGroupName(self):
        self.assertEqual(
            self.ctx['testNotificationGroup'].getName(),
            (1, 3),
            'bad name'
        )

    def testNotificationGroupDescription(self):
        self.assertEqual(
            self.ctx['testNotificationGroup'].getDescription(),
            'A collection of test notifications.',
            'bad DESCRIPTION'
        )

    def testNotificationGroupClass(self):
        self.assertEqual(
            self.ctx['testNotificationGroup'].__class__.__name__,
            'NotificationGroup',
            'bad SYNTAX class'
        )

if __name__ == '__main__': unittest.main()
