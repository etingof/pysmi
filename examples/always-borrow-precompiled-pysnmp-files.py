#
# Try to download (AKA borrow) precompiled pysnmp MIB file(s) 
# from a web-site.
# In this example no attempt is made to find and compile ASN.1
# MIB source.
#
# Fetched pysnmp MIB(s) are stored in a local directory.
#
from pysmi.reader.httpclient import HttpReader
from pysmi.searcher.pyfile import PyFileSearcher
from pysmi.borrower.pyfile import PyFileBorrower
from pysmi.writer.pyfile import PyFileWriter
from pysmi.parser.null import NullParser
from pysmi.codegen.null import NullCodeGen
from pysmi.compiler import MibCompiler
from pysmi import debug

#debug.setLogger(debug.Debug('compiler'))

inputMibs = [ 'BORROWED-MIB' ]

httpBorrowers = [
    ('mibs.snmplabs.com', 80, '/pysnmp/notexts/<mib>')
]
dstDirectory = '.pysnmp-mibs'

# Initialize compiler infrastructure

mibCompiler = MibCompiler(
    NullParser(), NullCodeGen(), PyFileWriter(dstDirectory)
)

# check compiled/borrowed MIBs in our own productions
mibCompiler.addSearchers(PyFileSearcher(dstDirectory))

# search for precompiled MIBs at Web sites
mibCompiler.addBorrowers(
    *[ PyFileBorrower(HttpReader(*x)) for x in httpBorrowers ]
)

# run MIB compilation
results = mibCompiler.compile(*inputMibs)

print('Results: %s' % ', '.join(['%s:%s' % (x, results[x]) for x in results]))
