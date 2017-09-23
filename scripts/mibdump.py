#!/usr/bin/env python
#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pysmi.sf.net/license.html
#
# SNMP SMI/MIB data management tool
#
import os
import sys
import getopt
from pysmi.reader import getReadersFromUrls
from pysmi.searcher import AnyFileSearcher, PyFileSearcher, PyPackageSearcher, StubSearcher
from pysmi.borrower import AnyFileBorrower, PyFileBorrower
from pysmi.writer import PyFileWriter, FileWriter, CallbackWriter
from pysmi.parser import SmiV1CompatParser
from pysmi.codegen import PySnmpCodeGen, JsonCodeGen, NullCodeGen
from pysmi.compiler import MibCompiler
from pysmi import debug
from pysmi import error

# Defaults
verboseFlag = True
mibSources = []
doFuzzyMatchingFlag = True
mibSearchers = []
mibStubs = []
mibBorrowers = []
dstFormat = None
dstDirectory = None
cacheDirectory = ''
nodepsFlag = False
rebuildFlag = False
dryrunFlag = False
genMibTextsFlag = False
keepTextsLayout = False
pyCompileFlag = True
pyOptimizationLevel = 0
ignoreErrorsFlag = False
buildIndexFlag = False
writeMibsFlag = True

helpMessage = """\
Usage: %s [--help]
      [--version]
      [--quiet]
      [--debug=<%s>]
      [--mib-source=<URI>]
      [--mib-searcher=<PATH|PACKAGE>]
      [--mib-stub=<MIB-NAME>]
      [--mib-borrower=<PATH>]
      [--destination-format=<FORMAT>]
      [--destination-directory=<DIRECTORY>]
      [--cache-directory=<DIRECTORY>]
      [--disable-fuzzy-source]
      [--no-dependencies]
      [--no-python-compile]
      [--python-optimization-level]
      [--ignore-errors]
      [--build-index]
      [--rebuild]
      [--dry-run]
      [--no-mib-writes]
      [--generate-mib-texts]
      [--keep-texts-layout]
      <MIB|URI> [<MIB|URI> [...]]]
Where:
    URI         - file, zip, http, https, ftp, sftp schemes are supported.
                  Use @mib@ placeholder token in URI to refer directly to
                  the required MIB module when source does not support
                  directory listing (e.g. HTTP).
    FORMAT      - pysnmp, json, null
    MIB or URI  - Either MIB module name or a URI pointing to a MIB source.
                  In the latter case all MIBs will be pulled and compiled.""" % (
    sys.argv[0],
    '|'.join([x for x in sorted(debug.flagMap)])
)

try:
    opts, inputMibsOrURIs = getopt.getopt(
        sys.argv[1:], 'hv',
        ['help', 'version', 'quiet', 'debug=',
        'mib-source=', 'mib-searcher=', 'mib-stub=', 'mib-borrower=',
        'destination-format=', 'destination-directory=', 'cache-directory=',
        'no-dependencies', 'no-python-compile',
        'python-optimization-level=', 'ignore-errors', 'build-index', 'rebuild',
        'dry-run', 'no-mib-writes', 'generate-mib-texts', 'disable-fuzzy-source',
        'keep-texts-layout']
    )

except getopt.GetoptError:
    if verboseFlag:
        sys.stderr.write('ERROR: %s\r\n%s\r\n' % (sys.exc_info()[1], helpMessage))

    sys.exit(1)

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
        from pysmi import __version__

        sys.stderr.write("""\
SNMP SMI/MIB library version %s, written by Ilya Etingof <etingof@gmail.com>
Python interpreter: %s
Software documentation and support at http://pysmi.sf.net
%s
""" % (__version__, sys.version, helpMessage))
        sys.exit(1)

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

    if opt[0] == '--mib-borrower':
        mibBorrowers.append((opt[1], genMibTextsFlag))

    if opt[0] == '--destination-format':
        dstFormat = opt[1]

    if opt[0] == '--destination-directory':
        dstDirectory = opt[1]

    if opt[0] == '--cache-directory':
        cacheDirectory = opt[1]

    if opt[0] == '--no-dependencies':
        nodepsFlag = True

    if opt[0] == '--no-python-compile':
        pyCompileFlag = False

    if opt[0] == '--python-optimization-level':
        try:
            pyOptimizationLevel = int(opt[1])

        except ValueError:
            sys.stderr.write('ERROR: known Python optimization levels: -1, 0, 1, 2\r\n%s\r\n' % helpMessage)
            sys.exit(-1)

    if opt[0] == '--ignore-errors':
        ignoreErrorsFlag = True

    if opt[0] == '--build-index':
        buildIndexFlag = True

    if opt[0] == '--rebuild':
        rebuildFlag = True

    if opt[0] == '--dry-run':
        dryrunFlag = True

    if opt[0] == '--no-mib-writes':
        writeMibsFlag = False

    if opt[0] == '--generate-mib-texts':
        genMibTextsFlag = True

    if opt[0] == '--disable-fuzzy-source':
        doFuzzyMatchingFlag = False

    if opt[0] == '--keep-texts-layout':
        keepTextsLayout = True

options = dict(
    noDeps=nodepsFlag,
    rebuild=rebuildFlag,
    dryRun=dryrunFlag,
    genTexts=genMibTextsFlag,
    textFilter=keepTextsLayout and (lambda symbol, text: text) or None,
    writeMibs=writeMibsFlag,
    ignoreErrors=ignoreErrorsFlag,
    fuzzyMatching=doFuzzyMatchingFlag
)

if inputMibsOrURIs:
    inputMibs = [os.path.basename(os.path.splitext(x)[0])
                 for x in inputMibsOrURIs
                 if '://' not in x]
    if inputMibs:
        mibSources.extend(list(set(['file://' + os.path.abspath(os.path.dirname(x))
                                    for x in inputMibs
                                    if os.path.sep in x])))

    inputURIs = getReadersFromUrls(*[uri for uri in inputMibsOrURIs if '://' in uri], **options)

else:
    sys.stderr.write('ERROR: MIB names / URIs not specified\r\n%s\r\n' % helpMessage)
    sys.exit(-1)

if not mibSources:
    mibSources = ['file:///usr/share/snmp/mibs',
                  'http://mibs.snmplabs.com/asn1/@mib@']

if not dstFormat:
    dstFormat = 'pysnmp'

if dstFormat == 'pysnmp':
    if not mibSearchers:
        mibSearchers = PySnmpCodeGen.defaultMibPackages

    if not mibStubs:
        mibStubs = [x for x in PySnmpCodeGen.baseMibs if x not in PySnmpCodeGen.fakeMibs]

    if not mibBorrowers:
        mibBorrowers = [('http://mibs.snmplabs.com/pysnmp/notexts/@mib@', False),
                        ('http://mibs.snmplabs.com/pysnmp/fulltexts/@mib@', True)]

    if not dstDirectory:
        dstDirectory = os.path.expanduser("~")
        if sys.platform[:3] == 'win':
            dstDirectory = os.path.join(dstDirectory, 'PySNMP Configuration', 'mibs')
        else:
            dstDirectory = os.path.join(dstDirectory, '.pysnmp', 'mibs')

    # Compiler infrastructure

    borrowers = [PyFileBorrower(x[1], genTexts=mibBorrowers[x[0]][1])
                 for x in enumerate(getReadersFromUrls(*[m[0] for m in mibBorrowers], **dict(lowcaseMatching=False)))]

    searchers = [PyFileSearcher(dstDirectory)]

    for mibSearcher in mibSearchers:
        searchers.append(PyPackageSearcher(mibSearcher))

    searchers.append(StubSearcher(*mibStubs))

    codeGenerator = PySnmpCodeGen()

    fileWriter = PyFileWriter(dstDirectory).setOptions(pyCompile=pyCompileFlag,
                                                       pyOptimizationLevel=pyOptimizationLevel)

elif dstFormat == 'json':
    if not mibStubs:
        mibStubs = JsonCodeGen.baseMibs

    if not mibBorrowers:
        mibBorrowers = [('http://mibs.snmplabs.com/json/notexts/@mib@', False),
                        ('http://mibs.snmplabs.com/json/fulltexts/@mib@', True)]

    if not dstDirectory:
        dstDirectory = os.path.join('.')

    # Compiler infrastructure

    borrowers = [AnyFileBorrower(x[1], genTexts=mibBorrowers[x[0]][1]).setOptions(exts=['.json'])
                 for x in enumerate(getReadersFromUrls(*[m[0] for m in mibBorrowers], **dict(lowcaseMatching=False)))]

    searchers = [AnyFileSearcher(dstDirectory).setOptions(exts=['.json']), StubSearcher(*mibStubs)]

    codeGenerator = JsonCodeGen()

    fileWriter = FileWriter(dstDirectory).setOptions(suffix='.json')

elif dstFormat == 'null':
    if not mibStubs:
        mibStubs = NullCodeGen.baseMibs

    if not mibBorrowers:
        mibBorrowers = [('http://mibs.snmplabs.com/null/notexts/@mib@', False),
                        ('http://mibs.snmplabs.com/null/fulltexts/@mib@', True)]

    if not dstDirectory:
        dstDirectory = ''

    # Compiler infrastructure

    codeGenerator = NullCodeGen()

    searchers = [StubSearcher(*mibStubs)]

    borrowers = [AnyFileBorrower(x[1], genTexts=mibBorrowers[x[0]][1])
                 for x in enumerate(getReadersFromUrls(*[m[0] for m in mibBorrowers], **dict(lowcaseMatching=False)))]

    fileWriter = CallbackWriter(lambda *x: None)

else:
    sys.stderr.write('ERROR: unknown destination format: %s\r\n%s\r\n' % (dstFormat, helpMessage))
    sys.exit(-1)

if verboseFlag:
    sys.stderr.write("""Source MIB repositories: %s
Borrow missing/failed MIBs from: %s
Existing/compiled MIB locations: %s
Compiled MIBs destination directory: %s
MIBs excluded from code generation: %s
MIBs to compile: %s
MIBs repositories to compile: %s
Destination format: %s
Parser grammar cache directory: %s
Also compile dependencies: %s
Rebuild MIBs regardless of age: %s
Dry run mode: %s
Create/update MIBs: %s
Byte-compile Python modules: %s (optimization level %s)
Ignore compilation errors: %s
Generate OID->MIB index: %s
Generate texts in MIBs: %s
Keep original texts layout: %s
Try various file names while searching for MIB module: %s
""" % (', '.join(mibSources),
       ', '.join([x[0] for x in mibBorrowers if x[1] == genMibTextsFlag]),
       ', '.join(mibSearchers),
       dstDirectory,
       ', '.join(sorted(mibStubs)),
       ', '.join(inputMibs),
       ', '.join([str(source) for source in inputURIs]),
       dstFormat,
       cacheDirectory or 'not used',
       nodepsFlag and 'no' or 'yes',
       rebuildFlag and 'yes' or 'no',
       dryrunFlag and 'yes' or 'no',
       writeMibsFlag and 'yes' or 'no',
       dstFormat == 'pysnmp' and pyCompileFlag and 'yes' or 'no',
       dstFormat == 'pysnmp' and pyOptimizationLevel and 'yes' or 'no',
       ignoreErrorsFlag and 'yes' or 'no',
       buildIndexFlag and 'yes' or 'no',
       genMibTextsFlag and 'yes' or 'no',
       keepTextsLayout and 'yes' or 'no',
       doFuzzyMatchingFlag and 'yes' or 'no'))

# Initialize compiler infrastructure

mibCompiler = MibCompiler(
    SmiV1CompatParser(tempdir=cacheDirectory),
    codeGenerator,
    fileWriter
)

try:
    mibCompiler.addSources(
        *getReadersFromUrls(*mibSources, **options)
    )

    mibCompiler.addSearchers(*searchers)

    mibCompiler.addBorrowers(*borrowers)

    processed = {}

    context = {}

    for inputMib in inputMibs:
        step = mibCompiler.compileOne(inputMib, context, **options)
        if verboseFlag:
            sys.stderr.write('Progress: %s\n' % ', '.join(['%s (%s)' % items for items in step.items()]))
        processed.update(step)

    if inputURIs:
        for step in mibCompiler.compileNext(*inputURIs, **options):
            if verboseFlag:
                sys.stderr.write('Progress: %s\n' % ', '.join(['%s (%s)' % items for items in step.items()]))
            processed.update(step)

    if buildIndexFlag:
        mibCompiler.buildIndex(
            processed, **options
        )

except error.PySmiError:
    sys.stderr.write('ERROR: %s\r\n' % sys.exc_info()[1])
    sys.exit(-1)

else:
    if verboseFlag:
        sys.stderr.write('%sreated/updated MIBs: %s\r\n' % (dryrunFlag and 'Would be c' or 'C', ', '.join(
            ['%s%s' % (x, x != processed[x].alias and ' (%s)' % processed[x].alias or '') for x in sorted(processed) if processed[x] == 'compiled'])))

        sys.stderr.write(
            'Up to date MIBs: %s\r\n' % ', '.join(['%s' % x for x in sorted(processed) if processed[x] == 'untouched']))

        sys.stderr.write('Just parsed MIBs: %s\r\n' % (', '.join(
            ['%s%s' % (x, x != processed[x].alias and ' (%s)' % processed[x].alias or '') for x in sorted(processed) if processed[x] == 'parsed'])))

        sys.stderr.write('Pre-compiled MIBs %sborrowed: %s\r\n' % (dryrunFlag and 'Would be ' or '', ', '.join(
            ['%s (%s)' % (x, processed[x].path) for x in sorted(processed) if processed[x] == 'borrowed'])))

        sys.stderr.write('Missing source MIBs: %s\r\n' % ', '.join(
            ['%s' % x for x in sorted(processed) if processed[x] == 'missing']))

        sys.stderr.write(
            'Failed but ignored MIBs: %s\r\n' % ', '.join(['%s' % x for x in sorted(processed) if processed[x] == 'unprocessed']))

        sys.stderr.write('Failed MIBs: %s\r\n' % ', '.join(
            ['%s (%s)' % (x, processed[x].error) for x in sorted(processed) if processed[x] == 'failed']))

    sys.exit(0)
