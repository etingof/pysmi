import sys
if sys.version_info[0:2] < (2, 7) or \
   sys.version_info[0:2] in ( (3, 0), (3, 1) ):
    try:
        import unittest2 as unittest
    except ImportError:
        import unittest
else:
    import unittest
from pysmi.parser.smi import parserFactory
from pysmi.codegen.pysnmp import PySnmpCodeGen
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
        self.mibInfo, pycode = PySnmpCodeGen().genCode(parserFactory()().parse(self.__class__.__doc__)[0], {}, genTexts=True)
        codeobj = compile(pycode, 'test', 'exec')
 
        mibBuilder = MibBuilder()
        mibBuilder.loadTexts = True

        self.ctx = { 'mibBuilder': mibBuilder }

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
            'Initial version',
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

if __name__ == '__main__': unittest.main()
