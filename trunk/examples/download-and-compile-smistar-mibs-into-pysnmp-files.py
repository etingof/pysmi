#
# Look up specific ASN.1 MIBs at configured Web and FTP sites,
# compile them into pysnmp form and save Python modules as plain-text
# files in a local directory.
#
# Try to support both SMIv1 and SMIv2 flavors of SMI as well as 
# popular deviations from official syntax found in the wild.
#
# In this example we disable automatic dependency checking on MIB
# compilation using noDeps flag.
#
# Also, we do not check if target file already exists thus MIB
# compilation occurs on every invocation.
#
from pysmi.reader.httpclient import HttpReader
from pysmi.reader.ftpclient import FtpReader
from pysmi.searcher.stub import StubSearcher
from pysmi.writer.pyfile import PyFileWriter
from pysmi.parser.smi import parserFactory
from pysmi.parser.dialect import smiV1Relaxed
from pysmi.codegen.pysnmp import PySnmpCodeGen, baseMibs
from pysmi.compiler import MibCompiler
from pysmi import debug

#debug.setLogger(debug.Debug('all'))

inputMibs = [ 'IF-MIB', 'IP-MIB' ]
httpSources = [ 
    ('mibs.snmplabs.com', 80, '/asn1/<mib>')
]
ftpSources = [
    ('ftp.cisco.com', '/pub/mibs/v1/<mib>')
]
dstDirectory = '.pysnmp-mibs'

# Initialize compiler infrastructure

mibCompiler = MibCompiler(
    parserFactory(**smiV1Relaxed)(), PySnmpCodeGen(), PyFileWriter(dstDirectory)
)

# search for source MIBs at Web and FTP sites
mibCompiler.addSources(*[ HttpReader(*x) for x in httpSources ])
mibCompiler.addSources(*[ FtpReader(*x) for x in ftpSources ])

# never recompile MIBs with MACROs
mibCompiler.addSearchers(StubSearcher(*baseMibs))

# run non-recursive MIB compilation
results = mibCompiler.compile(*inputMibs, noDeps=True)

print('Results: %s' % ', '.join(['%s:%s' % (x, results[x]) for x in results]))
