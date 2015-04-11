import test_moduleidentity_smiv2_pysnmp
import test_imports_smiv2_pysnmp
import test_agentcapabilities_smiv2_pysnmp
import test_modulecompliance_smiv2_pysnmp
import test_notificationgroup_smiv2_pysnmp
import test_notificationtype_smiv2_pysnmp
import test_objectgroup_smiv2_pysnmp
import test_objecttype_smiv2_pysnmp
import test_traptype_smiv2_pysnmp
import test_typedeclaration_smiv2_pysnmp
import test_typedeclaration_smiv1_pysnmp
import test_valuedeclaration_smiv2_pysnmp

testModules = [ x[1] for x in globals().items() if x[0][:5] == 'test_' ]

try:
    import unittest2 as unittest
except ImportError:
    import unittest

suite = unittest.TestSuite()
loader = unittest.TestLoader()

for m in testModules:
    suite.addTest(loader.loadTestsFromModule(m))

def runTests(): unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__': runTests()
