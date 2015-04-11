from pysmi.reader.localfile import FileReader
from pysmi.searcher.pyfile import PyFileSearcher
from pysmi.searcher.pypackage import PyPackageSearcher
from pysmi.searcher.stub import StubSearcher
from pysmi.writer.pyfile import PyFileWriter
from pysmi.parser.smiv2 import SmiV2Parser
from pysmi.codegen.pysnmp import PySnmpCodeGen, defaultMibPackages, baseMibs
from pysmi.compiler import MibCompiler
from pysmi import debug

#debug.setLogger(debug.Debug('all'))

inputMibs = [ 'IF-MIB' ]
srcDirectories = [ '/usr/share/snmp/mibs' ]
dstDirectory = '.pysnmp-mibs'

# Initialize compiler infrastructure

mibCompiler = MibCompiler(SmiV2Parser(),
                          PySnmpCodeGen(),
                          PyFileWriter(dstDirectory))

# search for source MIBs here
mibCompiler.addSources(*[ FileReader(x) for x in srcDirectories ])

# check compiled MIBs in our own productions
mibCompiler.addSearchers(PyFileSearcher(dstDirectory))
# ...and at default PySNMP MIBs packages
mibCompiler.addSearchers(*[ PyPackageSearcher(x) for x in defaultMibPackages ])

# never recompile MIBs with MACROs
mibCompiler.addSearchers(StubSearcher(*baseMibs))

# run [possibly recursive] MIB compilation
processed = mibCompiler.compile(*inputMibs, genTexts=False)

print('Created/updated MIBs: %s' % ', '.join(processed))
