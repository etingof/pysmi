"""
Compile SMIv1/v2 MIBs
+++++++++++++++++++++

Look up specific ASN.1 MIBs at configured local directories,
compile them into pysnmp form if not done yet and save Python
modules as plain-text files in a local directory.

Try to support both SMIv1 and SMIv2 flavors of SMI as well as
popular deviations from official syntax found in the wild.

When figuring out if compilation is needed, check all known
places where pysnmp MIBs could possibly be found.

You can force MIB re-compilation by passing rebuild flag to
MIB compiler (see below).

Default invocation of MIB compiler does not generate [potentially
large] comments and texts found in MIBs. If you need them in pysnmp
MIB modules, just pass genTexts flag to MIB compiler.
"""#
from pysmi.reader import FileReader
from pysmi.searcher import PyFileSearcher, PyPackageSearcher, StubSearcher
from pysmi.writer import PyFileWriter
from pysmi.parser import SmiStarParser
from pysmi.codegen import PySnmpCodeGen
from pysmi.compiler import MibCompiler

inputMibs = ['IF-MIB', 'IP-MIB']
srcDirectories = ['/usr/share/snmp/mibs']
dstDirectory = '.pysnmp-mibs'

# Initialize compiler infrastructure

mibCompiler = MibCompiler(SmiStarParser(),
                          PySnmpCodeGen(),
                          PyFileWriter(dstDirectory))

# search for source MIBs here
mibCompiler.addSources(*[FileReader(x) for x in srcDirectories])

# check compiled MIBs in our own productions
mibCompiler.addSearchers(PyFileSearcher(dstDirectory))
# ...and at default PySNMP MIBs packages
mibCompiler.addSearchers(*[PyPackageSearcher(x) for x in PySnmpCodeGen.defaultMibPackages])

# never recompile MIBs with MACROs
mibCompiler.addSearchers(StubSearcher(*PySnmpCodeGen.baseMibs))

# run [possibly recursive] MIB compilation
results = mibCompiler.compile(*inputMibs)  #, rebuild=True, genTexts=True)

print('Results: %s' % ', '.join(['%s:%s' % (x, results[x]) for x in results]))
