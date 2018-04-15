#!/usr/bin/env python
#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2018, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysmi/license.html
#
# SNMP SMI/MIB data management tool
#
import os
import sys
import getopt
from datetime import datetime
from pysmi.reader import FileReader, getReadersFromUrls
from pysmi.searcher import StubSearcher
from pysmi.writer import CallbackWriter
from pysmi.parser import SmiV1CompatParser
from pysmi.codegen import JsonCodeGen
from pysmi.compiler import MibCompiler
from pysmi import debug
from pysmi import error


# Defaults
verboseFlag = True
mibSources = []
doFuzzyMatchingFlag = True
mibSearchers = []
mibStubs = []
dstDirectory = None
cacheDirectory = ''
dryrunFlag = False
ignoreErrorsFlag = False

helpMessage = """\
Usage: %s [--help]
      [--version]
      [--quiet]
      [--debug=<%s>]
      [--mib-source=<URI>]
      [--mib-searcher=<PATH|PACKAGE>]
      [--mib-stub=<MIB-NAME>]
      [--destination-directory=<DIRECTORY>]
      [--cache-directory=<DIRECTORY>]
      [--ignore-errors]
      [--dry-run]
      <MIB-DIR> [MIB-DIR [...]]]
Where:
    URI      - file, zip, http, https, ftp, sftp schemes are supported.
               Use @mib@ placeholder token in URI to refer directly to
               the required MIB module when source does not support
               directory listing (e.g. HTTP).
""" % (
    sys.argv[0],
    '|'.join([x for x in sorted(debug.flagMap)])
)

try:
    opts, mibDirs = getopt.getopt(
        sys.argv[1:], 'hv',
        ['help', 'version', 'quiet', 'debug=',
        'mib-source=', 'mib-searcher=', 'mib-stub=', 'destination-directory=',
         'cache-directory=', 'ignore-errors', 'dry-run']
    )

except getopt.GetoptError:
    if verboseFlag:
        sys.stderr.write('ERROR: %s\r\n%s\r\n' % (sys.exc_info()[1], helpMessage))

    sys.exit(1)

for opt in opts:
    if opt[0] == '-h' or opt[0] == '--help':
        sys.stderr.write("""\
Synopsis:
  SNMP SMI/MIB files clean up tool
Documentation:
  http://snmplabs.com/pysmi
%s
""" % helpMessage)
        sys.exit(-1)

    if opt[0] == '-v' or opt[0] == '--version':
        from pysmi import __version__

        sys.stderr.write("""\
SNMP SMI/MIB library version %s, written by Ilya Etingof <etingof@gmail.com>
Python interpreter: %s
Software documentation and support at http://snmplabs.com/pysmi
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

    if opt[0] == '--destination-directory':
        dstDirectory = opt[1]

    if opt[0] == '--cache-directory':
        cacheDirectory = opt[1]

    if opt[0] == '--ignore-errors':
        ignoreErrorsFlag = True

if not mibSources:
    mibSources = ['file:///usr/share/snmp/mibs',
                  'http://mibs.snmplabs.com/asn1/@mib@']

if not mibDirs:
    sys.stderr.write('ERROR: source MIB directories not specified\r\n%s\r\n' % helpMessage)
    sys.exit(-1)

if not mibStubs:
    mibStubs = JsonCodeGen.baseMibs

if not dstDirectory:
    dstDirectory = os.path.join('.')

# Compiler infrastructure

searchers = [StubSearcher(*mibStubs)]

codeGenerator = JsonCodeGen()

mibParser = SmiV1CompatParser(tempdir=cacheDirectory)

for mibDir in mibDirs:

    if verboseFlag:
        sys.stderr.write('Processing directory "%s"...\r\n' % mibDir)

    context = {}

    fileWriter = CallbackWriter(lambda *x: None)

    mibCompiler = MibCompiler(
        mibParser,
        codeGenerator,
        fileWriter
    )

    mibCompiler.addSources(
        FileReader(mibDir, recursive=False, ignoreErrors=ignoreErrorsFlag),
        *getReadersFromUrls(*mibSources)
    )

    mibCompiler.addSearchers(*searchers)

    for mibFile in os.listdir(mibDir):

        if verboseFlag:
            sys.stderr.write('Processing file "%s"...\r\n' % os.path.join(mibDir, mibFile))

        try:
            processed = mibCompiler.compile(
                mibFile, **dict(noDeps=True, rebuild=True, ignoreErrors=ignoreErrorsFlag)
            )

        except error.PySmiError:
            sys.stderr.write('ERROR: %s\r\n' % sys.exc_info()[1])
            sys.exit(-1)

        for canonicalMibName in processed:
            if processed[canonicalMibName] == 'compiled':
                if canonicalMibName not in context:
                    context[canonicalMibName] = []

                try:
                    revision = datetime.strptime(processed[canonicalMibName].revision, '%Y-%m-%d %H:%M')

                except Exception:
                    revision = datetime.fromtimestamp(0)

                context[canonicalMibName].append((mibFile, revision))

                if verboseFlag:
                    sys.stderr.write('File "%s" contains MIB "%s"\r\n' % (
                        os.path.join(mibDir, mibFile), canonicalMibName))

    # rearrange MIBs in this directory

    for canonicalMibName, files in context.items():
        files = sorted(files, key=lambda x: x[1])
        filename, revision = files[-1]

        if filename != canonicalMibName:

            if verboseFlag:
                sys.stderr.write('Rename "%s" (revision "%s") -> "%s"\r\n' % (
                    os.path.join(mibDir, filename), revision,
                    os.path.join(mibDir, canonicalMibName)))

            # TODO: check for existing file and its revision
            try:
                os.rename(os.path.join(mibDir, filename), os.path.join(mibDir, canonicalMibName))

            except Exception as ex:
                sys.stderr.write('Failed to rename "%s" -> "%s": "%s"\r\n' % (
                    os.path.join(mibDir, filename),
                    os.path.join(mibDir, canonicalMibName),
                    ex))
                continue

        for filename, revision in files[:-1]:
            try:
                os.remove(os.path.join(mibDir, filename))

            except Exception as ex:
                sys.stderr.write('Failed to remove "%s": "%s"\r\n' % (os.path.join(mibDir, filename), ex))
                continue
