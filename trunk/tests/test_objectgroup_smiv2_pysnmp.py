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
        self.thisMib, self.otherMibs, pycode = PySnmpCodeGen().genCode(SmiV2Parser().parse(self.__class__.__doc__), genTexts=True)
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

if __name__ == '__main__': unittest.main()
