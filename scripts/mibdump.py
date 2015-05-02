#!/usr/bin/env python
#
# SNMP SMI/MIB data management tool
#
# Written by Ilya Etingof <ilya@glas.net>, 2015
#
import os
import sys
import getopt
try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse
from pysmi.reader.localfile import FileReader
from pysmi.reader.httpclient import HttpReader
from pysmi.reader.ftpclient import FtpReader
from pysmi.searcher.pyfile import PyFileSearcher
from pysmi.searcher.pypackage import PyPackageSearcher
from pysmi.searcher.stub import StubSearcher
from pysmi.writer.pyfile import PyFileWriter
from pysmi.parser.smiv1compat import SmiV1CompatParser
from pysmi.codegen.pysnmp import PySnmpCodeGen, defaultMibPackages, baseMibs
from pysmi.compiler import MibCompiler
from pysmi import debug
from pysmi import error

# Defaults
verboseFlag = True
mibSources = []
doFuzzyMatchingFlag = True
mibSearchers = []
mibStubs = []
dstFormat = 'pysnmp'
dstDirectory = os.path.join(os.path.expanduser("~"), '.pysnmp', 'mibs')
dstDirectory = os.path.expanduser("~")
if sys.platform[:3] == 'win':
    dstDirectory = os.path.join(dstDirectory, 'PySNMP Configuration', 'mibs')
else:
    dstDirectory = os.path.join(dstDirectory, '.pysnmp', 'mibs')
cacheDirectory = ''
nodepsFlag = False
rebuildFlag = False
dryrunFlag = False
genMibTextsFlag = False
ignoreErrorsFlag = False
buildIndexFlag = False

helpMessage = """\
Usage: %s [--help]
      [--version]
      [--quiet]
      [--debug=<%s>]
      [--mib-source=<url>]
      [--disable-fuzzy-source]
      [--mib-searcher=<path|package>]
      [--mib-stub=<mibname>]
      [--destination-format=<format>]
      [--destination-directory=<directory>]
      [--cache-directory=<directory>]
      [--no-dependencies]
      [--ignore-errors]
      [--build-index]
      [--rebuild]
      [--dry-run]
      [--generate-mib-texts]
      [ mibfile [ mibfile [...]]]
Where:
    url      - file, http, https, ftp, sftp schemes are supported. 
               Use <mib> placeholder token in URL location to refer
               to MIB module name requested.
    format   - pysnmp format is only supported.""" % (
          sys.argv[0],
          '|'.join([ x for x in sorted(debug.flagMap) ])
      )

try:
    opts, inputMibs = getopt.getopt(sys.argv[1:], 'hv',
        ['help', 'version', 'quiet', 'debug=',
         'mib-source=', 'mib-searcher=', 'mib-stub=', 
         'destination-format=', 'destination-directory=', 'cache-directory=',
         'no-dependencies', 'ignore-errors', 'build-index', 
         'rebuild', 'dry-run',
         'generate-mib-texts', 'disable-fuzzy-source' ]
    )
except Exception:
    if verboseFlag:
        sys.stderr.write('ERROR: %s\r\n%s\r\n' % (sys.exc_info()[1], helpMessage))
    sys.exit(-1)

for opt in opts:
    if opt[0] == '-h' or opt[0] == '--help':
        sys.stderr.write("""\
Synopsis:
  SNMP SMI/MIB files conversion tool
Documentation:
  http://pysmi.sourceforge.net
%s
""" % helpMessage)
        sys.exit(-1)
    if opt[0] == '-v' or opt[0] == '--version':
        sys.stderr.write("""\
SNMP SMI/MIB library version %s, written by Ilya Etingof <ilya@snmplabs.com>
Python interpreter: %s
Software documentation and support at http://pysmi.sf.net
%s
""" % (sys.version, helpMessage))
        sys.exit(-1)
    if opt[0] == '--quiet':
        verboseFlag = False
    if opt[0] == '--debug':
        debug.setLogger(debug.Debug(*opt[1].split(',')))
    if opt[0] == '--mib-source':
        mibSources.append(opt[1])
    if opt[0] == '--mib-searcher':
        mibSearchers.append(opt[1])
    if opt[0] == '--mib-stub':
        mibStubs.append(opt[1])
    if opt[0] == '--destination-format':
        dstFormat = opt[1]
    if opt[0] == '--destination-directory':
        dstDirectory = opt[1]
    if opt[0] == '--cache-directory':
        cacheDirectory = opt[1]
    if opt[0] == '--no-dependencies':
        nodepsFlag = True
    if opt[0] == '--ignore-errors':
        ignoreErrorsFlag = True
    if opt[0] == '--build-index':
        buildIndexFlag = True
    if opt[0] == '--rebuild':
        rebuildFlag = True
    if opt[0] == '--dry-run':
        dryrunFlag = True
    if opt[0] == '--generate-mib-texts':
        genMibTextsFlag = True
    if opt[0] == '--disable-fuzzy-source':
        doFuzzyMatchingFlag = False

if inputMibs:
    inputMibs = [ os.path.basename(os.path.splitext(x)[0]) for x in inputMibs ]
else:
    sys.stderr.write('ERROR: MIB modules names not specified\r\n%s\r\n' % helpMessage)
    sys.exit(-1)

if not mibSearchers:
    mibSearchers = defaultMibPackages

if not mibStubs:
    mibStubs = baseMibs

if not mibSources:
    mibSources = [ 'file:///usr/share/snmp/mibs',
                   'http://mibs.snmplabs.com/asn1/<mib>' ]

if verboseFlag:
    sys.stderr.write("""Source MIB repositories: %s
Existing/compiled MIB locations: %s
Compiled MIBs destination directory: %s
MIBs excluded from compilation: %s
MIBs to compile: %s
Destination format: %s
Parser grammar cache directory: %s
Also compile all relevant MIBs: %s
Rebuild MIBs regardless of age: %s
Do not create/update MIBs: %s
Ignore compilation errors: %s
Generate OID->MIB index: %s
Generate texts in MIBs: %s
Try various filenames while searching for MIB module: %s
""" % (', '.join(sorted(mibSources)),
       ', '.join(mibSearchers),
       dstDirectory,
       ', '.join(sorted(mibStubs)),
       ', '.join(sorted(inputMibs)),
       dstFormat,
       cacheDirectory or 'not used',
       nodepsFlag and 'no' or 'yes',
       rebuildFlag and 'yes' or 'no',
       dryrunFlag and 'yes' or 'no',
       ignoreErrorsFlag and 'yes' or 'no',
       buildIndexFlag and 'yes' or 'no',
       genMibTextsFlag and 'yes' or 'no',
       doFuzzyMatchingFlag and 'yes' or 'no'))

# Initialize compiler infrastructure

mibCompiler = MibCompiler(SmiV1CompatParser(tempdir=cacheDirectory), 
                          PySnmpCodeGen(),
                          PyFileWriter(dstDirectory))

try:
    for mibSource in mibSources:
        mibSource = urlparse.urlparse(mibSource)
        if not mibSource.scheme or mibSource.scheme == 'file':
            mibCompiler.addSources(FileReader(mibSource.path).setOptions(fuzzyMatching=doFuzzyMatchingFlag))
        elif mibSource.scheme in ('http', 'https'):
            mibCompiler.addSources(HttpReader(mibSource.hostname, mibSource.port or 80, mibSource.path, ssl=mibSource.scheme == 'https').setOptions(fuzzyMatching=doFuzzyMatchingFlag))
        elif mibSource.scheme in ('ftp', 'sftp'):
            mibCompiler.addSources(FtpReader(mibSource.hostname, mibSource.path, ssl=mibSource.scheme == 'sftp', port=mibSource.port or 21, user=mibSource.username or 'anonymous', password=mibSource.password or 'anonymous@').setOptions(fuzzyMatching=doFuzzyMatchingFlag))
        else:
            sys.stderr.write('ERROR: unsupported URL scheme %s\r\n%s\r\n' % (opt[1], helpMessage))
            sys.exit(-1)
        
    mibCompiler.addSearchers(PyFileSearcher(dstDirectory))

    for mibSearcher in mibSearchers:
        mibCompiler.addSearchers(PyPackageSearcher(mibSearcher))

    mibCompiler.addSearchers(StubSearcher(*mibStubs))

    processed = mibCompiler.compile(*inputMibs,
                                    noDeps=nodepsFlag,
                                    rebuild=rebuildFlag,
                                    dryRun=dryrunFlag,
                                    genTexts=genMibTextsFlag,
                                    ignoreErrors=ignoreErrorsFlag)

    if buildIndexFlag:
        mibCompiler.buildIndex(
            processed,
            dryRun=dryrunFlag,
            ignoreErrors=ignoreErrorsFlag
        )

except error.PySmiError:
    sys.stderr.write('ERROR: %s\r\n' % sys.exc_info()[1])
    sys.exit(-1)

else:
    if verboseFlag:
        sys.stderr.write('%sreated/updated MIBs: %s\r\n' % (dryrunFlag and 'Would be c' or 'C', ', '.join(['%s%s' % (x,x != processed[x].alias and ' (%s)' % processed[x].alias or '') for x in sorted(processed) if processed[x] == 'compiled'])))
        sys.stderr.write('Up to date MIBs: %s\r\n' % ', '.join(['%s' % x for x in sorted(processed) if processed[x] == 'untouched']))
        sys.stderr.write('Missing source MIBs: %s\r\n' % ', '.join(['%s' % x for x in sorted(processed) if processed[x] == 'missing']))
        sys.stderr.write('Ignored MIBs: %s\r\n' % ', '.join(['%s' % x for x in sorted(processed) if processed[x] == 'unprocessed']))
        sys.stderr.write('Failed MIBs: %s\r\n' % ', '.join(['%s (%s)' % (x,processed[x].exception) for x in sorted(processed) if processed[x] == 'failed']))

    sys.exit(0)
