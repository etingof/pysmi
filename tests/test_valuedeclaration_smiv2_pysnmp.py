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

class ValueDeclarationTestCase(unittest.TestCase):
    """
TEST-MIB DEFINITIONS ::= BEGIN
IMPORTS

  OBJECT-TYPE
    FROM SNMPv2-SMI;

-- simple values

testValue1  OBJECT IDENTIFIER ::= { 1 }
testValue2  OBJECT IDENTIFIER ::= { testValue1 3 }
testValue3  OBJECT IDENTIFIER ::= { 1 3 6 1 2 }

-- testValue01  INTEGER ::= 123
-- testValue02  INTEGER ::= -123
-- testValue04  OCTET STRING ::= h'test string'
-- testValue05  INTEGER ::= testValue01
-- testValue06  OCTET STRING ::= "test string"
-- testValue07  OCTET STRING ::= b'010101'

-- application syntax

-- testValue03  Integer32 ::= 123
-- testValue03  Counter32 ::= 123
-- testValue03  Gauge32 ::= 123
-- testValue03  Unsigned32 ::= 123
-- testValue03  TimeTicks ::= 123
-- testValue03  Opaque ::= "0123"
-- testValue03  Counter64 ::= 123456789123456789
-- testValue03  IpAddress ::= "127.0.0.1"

END
 """

    def setUp(self):
        self.mibInfo, pycode = PySnmpCodeGen().genCode(SmiV2Parser().parse(self.__class__.__doc__), genTexts=True)
        codeobj = compile(pycode, 'test', 'exec')

        mibBuilder = MibBuilder()
        mibBuilder.loadTexts = True

        self.ctx = { 'mibBuilder': mibBuilder }

        exec(codeobj, self.ctx, self.ctx)

    def testValueDeclarationSymbol(self):
        self.assertTrue(
            'testValue1' in self.ctx and \
                 'testValue2' in self.ctx and \
                 'testValue3' in self.ctx,
            'symbol not present'
        )

    def testValueDeclarationName1(self):
        self.assertEqual(
            self.ctx['testValue1'].getName(),
            (1,),
            'bad value'
        )

    def testValueDeclarationName2(self):
        self.assertEqual(
            self.ctx['testValue2'].getName(),
            (1, 3),
            'bad value'
        )

    def testValueDeclarationName3(self):
        self.assertEqual(
            self.ctx['testValue3'].getName(),
            (1, 3, 6, 1, 2),
            'bad value'
        )

if __name__ == '__main__': unittest.main()
