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
        ast = parserFactory()().parse(self.__class__.__doc__)[0]
        mibInfo, symtable = SymtableCodeGen().genCode(ast, {}, genTexts=True)
        self.mibInfo, pycode = PySnmpCodeGen().genCode(ast, { mibInfo.name: symtable }, genTexts=True)
        codeobj = compile(pycode, 'test', 'exec')

        self.ctx = { 'mibBuilder': MibBuilder() }

        exec(codeobj, self.ctx, self.ctx)

    def testModuleImportsRequiredMibs(self):
        self.assertTupleEqual(
            self.mibInfo.imported,
            ('SNMP-FRAMEWORK-MIB', 'SNMPv2-CONF', 'SNMPv2-SMI', 'SNMPv2-TC'),
            'imported MIBs not reported'
        )

    def testModuleCheckImportedSymbol(self):
        self.assertTrue(
            'SnmpAdminString' in self.ctx,
            'imported symbol not present'
        )

if __name__ == '__main__': unittest.main()
