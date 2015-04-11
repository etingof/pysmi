try:
    import unittest2 as unittest
except ImportError:
    import unittest
from pysmi.parser.smiv2 import SmiV2Parser
from pysnmp.smi.builder import MibBuilder

class NotificationTypeTestCase(unittest.TestCase):
    """
TEST-MIB DEFINITIONS ::= BEGIN
IMPORTS
  NOTIFICATION-TYPE
    FROM SNMPv2-SMI;

testNotificationType NOTIFICATION-TYPE
   OBJECTS         {
                        testChangeConfigType,
                        testChangeConfigValue
                    }
    STATUS          current
    DESCRIPTION
        "A collection of test notification types."
 ::= { 1 3 }

END
 """

    def setUp(self):
        self.otherMibs, pycode = SmiV2Parser().parse(self.__class__.__doc__)
        codeobj = compile(pycode, 'test', 'exec')

        mibBuilder = MibBuilder()
        mibBuilder.loadTexts = True

        self.ctx = { 'mibBuilder': mibBuilder }

        exec(codeobj, self.ctx, self.ctx)

    def testNotificationTypeSymbol(self):
        self.assertTrue(
            'testNotificationType' in self.ctx,
            'symbol not present'
        )

    def testNotificationTypeName(self):
        self.assertEqual(
            self.ctx['testNotificationType'].getName(),
            (1, 3),
            'bad name'
        )

    def testNotificationTypeDescription(self):
        self.assertEqual(
            self.ctx['testNotificationType'].getDescription(),
            'A collection of test notification types.',
            'bad DESCRIPTION'
        )

    def testNotificationTypeClass(self):
        self.assertEqual(
            self.ctx['testNotificationType'].__class__.__name__,
            'NotificationType',
            'bad SYNTAX class'
        )

if __name__ == '__main__': unittest.main()
