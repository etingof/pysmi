#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2016, Ilya Etingof <ilya@glas.net>
# License: http://pysmi.sf.net/license.html
#
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
from pysmi.codegen.symtable import SymtableCodeGen
from pysnmp.smi.builder import MibBuilder

class TypeDeclarationTestCase(unittest.TestCase):
    """
TEST-MIB DEFINITIONS ::= BEGIN
IMPORTS

  IpAddress,
  Counter32,
  Gauge32,
  TimeTicks,
  Opaque,
  Integer32,
  Unsigned32,
  Counter64
    FROM SNMPv2-SMI

  TEXTUAL-CONVENTION
    FROM SNMPv2-TC;

-- simple types
TestTypeInteger ::= INTEGER
TestTypeOctetString ::= OCTET STRING
TestTypeObjectIdentifier ::= OBJECT IDENTIFIER

-- application types
TestTypeIpAddress ::= IpAddress
TestTypeInteger32 ::= Integer32
TestTypeCounter32 ::= Counter32
TestTypeGauge32 ::= Gauge32
TestTypeTimeTicks ::= TimeTicks
TestTypeOpaque ::= Opaque
TestTypeCounter64 ::= Counter64
TestTypeUnsigned32 ::= Unsigned32

-- constrained subtypes

TestTypeEnum ::= INTEGER {
                    noResponse(-1),
                    noError(0),
                    tooBig(1)
                }
TestTypeSizeRangeConstraint ::= OCTET STRING (SIZE (0..255))
TestTypeSizeConstraint ::= OCTET STRING (SIZE (8 | 11))
TestTypeRangeConstraint ::= INTEGER (0..2)
TestTypeSingleValueConstraint ::= INTEGER (0|2|4)

TestTypeBits ::= BITS {
                    sunday(0),
                    monday(1),
                    tuesday(2),
                    wednesday(3),
                    thursday(4),
                    friday(5),
                    saturday(6)
                }


TestTextualConvention ::= TEXTUAL-CONVENTION
    DISPLAY-HINT "1x:"
    STATUS       current
    DESCRIPTION
            "Test TC"
    REFERENCE
            "Test reference"
    SYNTAX       OCTET STRING

END
 """

    def setUp(self):
        ast = parserFactory()().parse(self.__class__.__doc__)[0]
        mibInfo, symtable = SymtableCodeGen().genCode(ast, {}, genTexts=True)
        self.mibInfo, pycode = PySnmpCodeGen().genCode(ast, { mibInfo.name: symtable }, genTexts=True)
        codeobj = compile(pycode, 'test', 'exec')

        mibBuilder = MibBuilder()
        mibBuilder.loadTexts = True

        self.ctx = { 'mibBuilder': mibBuilder }

        exec(codeobj, self.ctx, self.ctx)

    def protoTestSymbol(self, symbol, klass):
        self.assertTrue(
            symbol in self.ctx, 'symbol %s not present' % symbol
        )

    def protoTestClass(self, symbol, klass):
        self.assertEqual(
            self.ctx[symbol].__bases__[0].__name__, klass,
            'expected class %s, got %s at %s' % (klass, self.ctx[symbol].__bases__[0].__name__, symbol)
        )

    def TestTextualConventionSymbol(self):
        self.assertTrue(
            'TestTextualConvention' in self.ctx,
            'symbol not present'
        )

    def TestTextualConventionDisplayHint(self):
        self.assertEqual(
            self.ctx['TestTextualConvention'].getDisplayHint(),
            '1x:',
            'bad DISPLAY-HINT'
        )

    def TestTextualConventionStatus(self):
        self.assertEqual(
            self.ctx['TestTextualConvention'].getStatus(),
            'current',
            'bad STATUS'
        )

    def TestTextualConventionDescription(self):
        self.assertEqual(
            self.ctx['TestTextualConvention'].getDescription(),
            'Test TC',
            'bad DESCRIPTION'
        )

    def TestTextualConventionReference(self):
        self.assertEqual(
            self.ctx['TestTextualConvention'].getReference(),
            'Test reference',
            'bad REFERENCE'
        )

    def TestTextualConventionClass(self):
        self.assertEqual(
            self.ctx['TestTextualConvention'].__class__.__name__,
            'TextualConvention',
            'bad SYNTAX class'
        )

# populate test case class with per-type methods

typesMap = (
    ('TestTypeInteger', 'Integer'),
    ('TestTypeOctetString', 'OctetString'),
    ('TestTypeObjectIdentifier', 'ObjectIdentifier'),
    ('TestTypeIpAddress', 'IpAddress'),
    ('TestTypeInteger32', 'Integer32'),
    ('TestTypeCounter32', 'Counter32'),
    ('TestTypeGauge32', 'Gauge32'),
    ('TestTypeTimeTicks', 'TimeTicks'),
    ('TestTypeOpaque', 'Opaque'),
    ('TestTypeCounter64', 'Counter64'),
    ('TestTypeUnsigned32', 'Unsigned32'),
    ('TestTypeTestTypeEnum', 'Integer'),
    ('TestTypeSizeRangeConstraint', 'OctetString'),
    ('TestTypeSizeConstraint', 'OctetString'),
    ('TestTypeRangeConstraint', 'Integer'),
    ('TestTypeSingleValueConstraint', 'Integer')
)

def decor(func, symbol, klass):
    def inner(self):
        func(self, symbol, klass)
    return inner

for s, k in typesMap:
    setattr(TypeDeclarationTestCase, 'testTypeDeclaration'+k+'SymbolTestCase',
            decor(TypeDeclarationTestCase.protoTestSymbol, s, k))
    setattr(TypeDeclarationTestCase, 'testTypeDeclaration'+k+'ClassTestCase',
            decor(TypeDeclarationTestCase.protoTestClass, s, k))

# XXX constraints flavor not checked
        
if __name__ == '__main__': unittest.main()
