#
# Look up specific ASN.1 MIBs at configured Web/FTP sites.
# If no required MIB is found or its compilation fails for
# some reason, attempt to download precompiled version of
# failed MIB and store it locally as if we had compiled it.
#
from pysmi.reader.httpclient import HttpReader
from pysmi.searcher.pyfile import PyFileSearcher
from pysmi.searcher.stub import StubSearcher
from pysmi.borrower.pyfile import PyFileBorrower
from pysmi.writer.pyfile import PyFileWriter
from pysmi.parser.smi import parserFactory
from pysmi.parser.dialect import smiV1Relaxed
from pysmi.codegen.pysnmp import PySnmpCodeGen, baseMibs
from pysmi.compiler import MibCompiler
from pysmi import debug

# debug.setLogger(debug.Debug('borrower', 'reader', 'searcher'))

inputMibs = ['BORROWED-MIB']
httpSources = [ 
    ('mibs.snmplabs.com', 80, '/asn1/@mib@')
]
httpBorrowers = [
    ('mibs.snmplabs.com', 80, '/pysnmp/notexts/@mib@')
]
dstDirectory = '.pysnmp-mibs'

# Initialize compiler infrastructure

mibCompiler = MibCompiler(
    parserFactory(**smiV1Relaxed)(), PySnmpCodeGen(), PyFileWriter(dstDirectory)
)

# search for source MIBs at Web sites
mibCompiler.addSources(*[HttpReader(*x) for x in httpSources])

# never recompile MIBs with MACROs
mibCompiler.addSearchers(StubSearcher(*baseMibs))

# check compiled/borrowed MIBs in our own productions
mibCompiler.addSearchers(PyFileSearcher(dstDirectory))

# search for compiled MIBs at Web sites if source is not available or broken
mibCompiler.addBorrowers(*[PyFileBorrower(HttpReader(*x)).setOptions(genTexts=False) for x in httpBorrowers])

# run non-recursive MIB compilation
results = mibCompiler.compile(*inputMibs)

print('Results: %s' % ', '.join(['%s:%s' % (x, results[x]) for x in results]))
