#
# Look up specific ASN.1 MIBs at configured local directories,
# compile them into pysnmp form if not done yet and save Python
# modules as plain-text files in a local directory.
#
# Try to support both SMIv1 and SMIv2 flavors of SMI as well as
# popular deviations from official syntax found in the wild.
#
# When figuring out if compilation is needed, check all known
# places where pysnmp MIBs could possibly be found.
#
# You can force MIB re-compilation by passing rebuild flag to
# MIB compiler (see below).
#
# Default invocation of MIB compiler does not generate [potentially
# large] comments and texts found in MIBs. If you need them in pysnmp
# MIB modules, just pass genTexts flag to MIB compiler.
# 
from pysmi.reader.localfile import FileReader
from pysmi.searcher.pyfile import PyFileSearcher
from pysmi.searcher.pypackage import PyPackageSearcher
from pysmi.searcher.stub import StubSearcher
from pysmi.writer.pyfile import PyFileWriter
from pysmi.parser.smi import parserFactory
from pysmi.parser.dialect import smiV1Relaxed
from pysmi.codegen.pysnmp import PySnmpCodeGen, defaultMibPackages, baseMibs
from pysmi.compiler import MibCompiler
from pysmi import debug

# debug.setLogger(debug.Debug('reader', 'compiler'))

inputMibs = ['IF-MIB', 'IP-MIB']
srcDirectories = ['/usr/share/snmp/mibs']
dstDirectory = '.pysnmp-mibs'

# Initialize compiler infrastructure

mibCompiler = MibCompiler(parserFactory(**smiV1Relaxed)(),
                          PySnmpCodeGen(),
                          PyFileWriter(dstDirectory))

# search for source MIBs here
mibCompiler.addSources(*[FileReader(x) for x in srcDirectories])

# check compiled MIBs in our own productions
mibCompiler.addSearchers(PyFileSearcher(dstDirectory))
# ...and at default PySNMP MIBs packages
mibCompiler.addSearchers(*[PyPackageSearcher(x) for x in defaultMibPackages])

# never recompile MIBs with MACROs
mibCompiler.addSearchers(StubSearcher(*baseMibs))

# run [possibly recursive] MIB compilation
results = mibCompiler.compile(*inputMibs)  #, rebuild=True, genTexts=True)

print('Results: %s' % ', '.join(['%s:%s' % (x, results[x]) for x in results]))
