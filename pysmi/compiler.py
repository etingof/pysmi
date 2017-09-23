#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pysmi.sf.net/license.html
#
import sys
import os
import time
import itertools

try:
    from pwd import getpwuid
except ImportError:
    # noinspection PyPep8
    getpwuid = lambda x: ['<unknown>']
from pysmi import __name__ as packageName
from pysmi import __version__ as packageVersion
from pysmi.mibinfo import MibInfo
from pysmi.codegen.symtable import SymtableCodeGen
from pysmi import error
from pysmi import debug


class MibStatus(str):
    """Indicate MIB transformation result.

    *MibStatus* is a subclass of Python string type. Some additional
    attributes may be set to indicate the details.

    The following *MibStatus* class instances are defined:

    * *compiled* - MIB is successfully transformed
    * *untouched* - fresh transformed version of this MIB already exisits
    * *failed* - MIB transformation failed. *error* attribute carries details.
    * *unprocessed* - MIB transformation required but waived for some reason
    * *missing* - ASN.1 MIB source can't be found
    * *borrowed* - MIB transformation failed but pre-transformed version was used
    """

    def setOptions(self, **kwargs):
        n = self.__class__(self)
        for k in kwargs:
            setattr(n, k, kwargs[k])
        return n


statusParsed = MibStatus('parsed')
statusCompiled = MibStatus('compiled')
statusUntouched = MibStatus('untouched')
statusFailed = MibStatus('failed')
statusUnprocessed = MibStatus('unprocessed')
statusMissing = MibStatus('missing')
statusBorrowed = MibStatus('borrowed')


class MibCompiler(object):
    """Top-level, user-facing, composite MIB compiler object.

    MibCompiler implements high-level MIB transformation processing logic.
    It executes its actions by calling the following specialized objects:

      * *readers* - to acquire ASN.1 MIB data
      * *searchers* - to see if transformed MIB already exists and no processing is necessary
      * *parser* - to parse ASN.1 MIB into AST
      * *code generator* - to perform actual MIB transformation
      * *borrowers* - to fetch pre-transformed MIB if transformation is impossible
      * *writer* - to store transformed MIB data

    Required components must be passed to MibCompiler on instantiation. Those
    components are: *parser*, *codegenerator* and *writer*.

    Optional components could be set or modified at later phases of MibCompiler
    life. Unlike singular, required components, optional one can be present
    in sequences to address many possible sources of data. They are
    *readers*, *searchers* and *borrowers*.

    Examples: ::

        from pysmi.reader.localfile import FileReader
        from pysmi.searcher.pyfile import PyFileSearcher
        from pysmi.searcher.pypackage import PyPackageSearcher
        from pysmi.searcher.stub import StubSearcher
        from pysmi.writer.pyfile import PyFileWriter
        from pysmi.parser.smi import SmiV2Parser
        from pysmi.codegen.pysnmp import PySnmpCodeGen, baseMibs

        mibCompiler = MibCompiler(SmiV2Parser(),
                                  PySnmpCodeGen(),
                                  PyFileWriter('/tmp/pysnmp/mibs'))

        mibCompiler.addSources(FileReader('/usr/share/snmp/mibs'))

        mibCompiler.addSearchers(PyFileSearcher('/tmp/pysnmp/mibs'))
        mibCompiler.addSearchers(PyPackageSearcher('pysnmp.mibs'))

        mibCompiler.addSearchers(StubSearcher(*baseMibs))

        results = mibCompiler.compile('IF-MIB', 'IP-MIB')

    """
    indexFile = 'index'

    MAX_SYMTABLE_SIZE = 50

    def __init__(self, parser, codegen, writer):
        """Creates an instance of *MibCompiler* class.

           Args:
               parser: ASN.1 MIB parser object
               codegen: MIB transformation object
               writer: transformed MIB storing object
        """
        self._parser = parser
        self._codegen = codegen
        self._symbolgen = SymtableCodeGen()
        self._writer = writer
        self._sources = []
        self._searchers = []
        self._borrowers = []

    def addSources(self, *sources):
        """Add more ASN.1 MIB source repositories.

        MibCompiler.compile will invoke each of configured source objects
        in order of their addition asking each to fetch MIB module specified
        by name.

        Args:
            sources: reader object(s)

        Returns:
            reference to itself (can be used for call chaining)

        """
        self._sources.extend(sources)

        debug.logger & debug.flagCompiler and debug.logger(
            'current MIB source(s): %s' % ', '.join([str(x) for x in self._sources]))

        return self

    def addSearchers(self, *searchers):
        """Add more transformed MIBs repositories.

        MibCompiler.compile will invoke each of configured searcher objects
        in order of their addition asking each if already transformed MIB
        module already exists and is more recent than specified.

        Args:
            searchers: searcher object(s)

        Returns:
            reference to itself (can be used for call chaining)

        """
        self._searchers.extend(searchers)

        debug.logger & debug.flagCompiler and debug.logger(
            'current compiled MIBs location(s): %s' % ', '.join([str(x) for x in self._searchers]))

        return self

    def addBorrowers(self, *borrowers):
        """Add more transformed MIBs repositories to borrow MIBs from.

        Whenever MibCompiler.compile encounters MIB module which neither of
        the *searchers* can find or fetched ASN.1 MIB module can not be
        parsed (due to syntax errors), these *borrowers* objects will be
        invoked in order of their addition asking each if already transformed
        MIB can be fetched (borrowed).

        Args:
            borrowers: borrower object(s)

        Returns:
            reference to itself (can be used for call chaining)

        """
        self._borrowers.extend(borrowers)

        debug.logger & debug.flagCompiler and debug.logger(
            'current MIB borrower(s): %s' % ', '.join([str(x) for x in self._borrowers]))

        return self

    def _compileFileContents(self, fileContents, context, depth=0, **options):

        processed = {}

        try:
            symbolTableMap = context['symbols']

        except KeyError:
            symbolTableMap = context['symbols'] = {}

        fileInfo, fileData = fileContents

        debug.logger & debug.flagCompiler and debug.logger(
            'compiling MIB file %s, stack depth %d' % (fileInfo.name, depth))

        try:
            mibTrees = self._parser.parse(fileData)

        except error.PySmiError:
            exc_class, exc, tb = sys.exc_info()
            exc.mibname = fileInfo.name
            exc.msg += ' at MIB %s' % fileInfo.name

            processed[fileInfo.name] = statusFailed.setOptions(
                path=fileInfo.path,
                file=fileInfo.file,
                alias=fileInfo.name,
                error=exc
            )
            return processed

        for mibTree in mibTrees:

            try:
                mibInfo, symbolTable = self._symbolgen.genCode(
                    mibTree, symbolTableMap
                )

            except error.PySmiError:
                exc_class, exc, tb = sys.exc_info()
                exc.mibname = fileInfo.name
                exc.msg += ' at MIB %s' % fileInfo.name

                debug.logger & debug.flagCompiler and debug.logger('%serror %s' % (
                    options.get('ignoreErrors') and 'ignoring ' or 'failing on ', exc))

                processed[fileInfo.name] = statusFailed.setOptions(
                    path=fileInfo.path,
                    file=fileInfo.file,
                    alias=fileInfo.name,
                    error=exc
                )

                continue

            # By this moment we know canonical MIB name
            if fileInfo.name in processed:
                del processed[fileInfo.name]

            if mibInfo.name not in symbolTable:
                symbolTableMap[mibInfo.name] = symbolTable

            debug.logger & debug.flagCompiler and debug.logger(
                '%s (%s) read from %s, immediate dependencies: %s' % (
                    mibInfo.name, fileInfo.name, fileInfo.path, ', '.join(mibInfo.imported) or '<none>'))

            for mibname in mibInfo.imported:
                if mibname in symbolTableMap:
                    continue

                processed.update(
                    self.compileOne(mibname, context, depth + 1, **options)
                )

                if mibname not in symbolTableMap:
                    processed[mibInfo.name] = statusFailed.setOptions(
                        path=fileInfo.path,
                        file=fileInfo.file,
                        alias=fileInfo.name,
                        error=error.PySmiError(msg='failed dependency %s' % mibname)
                    )

                    debug.logger & debug.flagCompiler and debug.logger(
                        'failing on unresolved dependency %s of %s from %s, %s' % (
                            mibname, mibInfo.name, fileInfo.name, fileInfo.path)
                    )

                    return processed

            processed[mibInfo.name] = statusParsed.setOptions(
                path=fileInfo.path,
                file=fileInfo.file,
                alias=fileInfo.name
            )

            if depth and options.get('noDeps'):
                return processed

            #
            # See if we have this MIB already built and available
            #

            debug.logger & debug.flagCompiler and debug.logger('checking if %s requires updating' % mibInfo.name)

            for searcher in self._searchers:
                try:
                    searcher.fileExists(mibInfo.name, fileInfo.mtime, rebuild=options.get('rebuild'))

                except error.PySmiFileNotFoundError:
                    debug.logger & debug.flagCompiler and debug.logger(
                        'no compiled MIB %s available through %s' % (mibInfo.name, searcher))
                    continue

                except error.PySmiFileNotModifiedError:
                    debug.logger & debug.flagCompiler and debug.logger(
                        'will be using existing compiled MIB %s found by %s' % (mibInfo.name, searcher))
                    processed[mibInfo.name] = statusUntouched.setOptions(
                        path=fileInfo.path,
                        file=fileInfo.file,
                        alias=fileInfo.name
                    )
                    return processed

                except error.PySmiError:
                    exc_class, exc, tb = sys.exc_info()
                    exc.searcher = searcher
                    exc.mibname = mibInfo.name
                    exc.msg += ' at MIB %s' % mibInfo.name
                    debug.logger & debug.flagCompiler and debug.logger('error from %s: %s' % (searcher, exc))
                    continue

            else:
                debug.logger & debug.flagCompiler and debug.logger(
                    'no suitable compiled MIB %s found anywhere' % mibInfo.name)

            debug.logger & debug.flagCompiler and debug.logger(
                'no compiled MIB %s available anywhere' % mibInfo.name)

            #
            # Generate code for parsed MIB
            #

            debug.logger & debug.flagCompiler and debug.logger('compiling %s read from %s' % (mibInfo.name, fileInfo.path))

            comments = [
                'ASN.1 source %s' % fileInfo.path,
                'Produced by %s-%s at %s' % (packageName, packageVersion, time.asctime()),
                'On host %s platform %s version %s by user %s' % (
                    hasattr(os, 'uname') and os.uname()[1] or '?', hasattr(os, 'uname') and os.uname()[0] or '?',
                    hasattr(os, 'uname') and os.uname()[2] or '?',
                    hasattr(os, 'getuid') and getpwuid(os.getuid())[0] or '?'),
                'Using Python version %s' % sys.version.split('\n')[0]
            ]

            try:
                mibInfo, mibData = self._codegen.genCode(
                    mibTree,
                    symbolTableMap,
                    comments=comments,
                    genTexts=options.get('genTexts'),
                    textFilter=options.get('textFilter')
                )

                debug.logger & debug.flagCompiler and debug.logger(
                    '%s read from %s and compiled by %s' % (mibInfo.name, fileInfo.path, self._writer))

            except error.PySmiError:
                exc_class, exc, tb = sys.exc_info()
                exc.handler = self._codegen
                exc.mibname = mibInfo.name
                exc.msg += ' at MIB %s' % mibInfo.name

                debug.logger & debug.flagCompiler and debug.logger('error from %s: %s' % (self._codegen, exc))

                processed[mibInfo.name] = statusFailed.setOptions(error=exc)

            else:
                processed[mibInfo.name] = statusCompiled.setOptions(
                    path=fileInfo.path,
                    file=fileInfo.file,
                    alias=fileInfo.name,
                    oid=mibInfo.oid,
                    oids=mibInfo.oids,
                    identity=mibInfo.identity,
                    enterprise=mibInfo.enterprise,
                    compliance=mibInfo.compliance,
                )

            #
            # Try to borrow pre-compiled MIB if compilation fails
            #

            if processed[mibInfo.name] == statusFailed:

                for borrower in self._borrowers:
                    debug.logger & debug.flagCompiler and debug.logger('trying to borrow %s from %s' % (mibInfo.name, borrower))
                    try:
                        fileInfo, fileData = borrower.getData(
                            mibInfo.name,
                            genTexts=options.get('genTexts')
                        )

                        mibInfo, mibData = MibInfo(name=mibInfo.name, imported=[]), fileData

                        debug.logger & debug.flagCompiler and debug.logger('%s borrowed with %s' % (mibInfo.name, borrower))
                        break

                    except error.PySmiError:
                        debug.logger & debug.flagCompiler and debug.logger('error from %s: %s' % (borrower, sys.exc_info()[1]))

                else:
                    return processed

                #
                # We can borrow this MIB, but doo we want to?
                #

                debug.logger & debug.flagCompiler and debug.logger(
                    'checking if failed MIB %s requires borrowing' % mibInfo.name)

                for searcher in self._searchers:
                    try:
                        searcher.fileExists(mibInfo.name, fileInfo.mtime, rebuild=options.get('rebuild'))

                    except error.PySmiFileNotFoundError:
                        debug.logger & debug.flagCompiler and debug.logger(
                            'no compiled MIB %s available through %s' % (mibInfo.name, searcher))
                        continue

                    except error.PySmiFileNotModifiedError:
                        debug.logger & debug.flagCompiler and debug.logger(
                            'will be using existing compiled MIB %s found by %s' % (mibInfo.name, searcher))
                        processed[mibInfo.name] = statusUntouched
                        return processed

                    except error.PySmiError:
                        exc_class, exc, tb = sys.exc_info()
                        exc.searcher = searcher
                        exc.mibname = mibInfo.name
                        exc.msg += ' at MIB %s' % mibInfo.name

                        debug.logger & debug.flagCompiler and debug.logger('error from %s: %s' % (searcher, exc))

                        continue

                debug.logger & debug.flagCompiler and debug.logger('will use borrowed MIB %s' % mibInfo.name)

                processed[mibInfo.name] = statusBorrowed.setOptions(
                    path=fileInfo.path,
                    file=fileInfo.file,
                    alias=fileInfo.name
                )

            #
            # Store compiled or borrowed MIB
            #

            if not options.get('writeMibs', True):
                return processed

            try:
                self._writer.putData(
                    mibInfo.name, mibData, dryRun=options.get('dryRun')
                )

            except error.PySmiError:
                exc_class, exc, tb = sys.exc_info()
                exc.handler = self._codegen
                exc.mibname = mibInfo.name
                exc.msg += ' at MIB %s' % mibInfo.name

                debug.logger & debug.flagCompiler and debug.logger('error %s from %s' % (exc, self._writer))

                processed[mibInfo.name] = statusFailed.setOptions(
                    path=fileInfo.path,
                    file=fileInfo.file,
                    alias=fileInfo.name,
                    error=exc
                )

            debug.logger & debug.flagCompiler and debug.logger('%s stored by %s' % (mibInfo.name, self._writer))

        return processed

    def compileOne(self, mibname, context, depth=0, **options):
        """Transform one MIB and (optionally) its dependencies.

        The *compileOne* method should be invoked when *MibCompiler* object
        is operational meaning at least *sources* are specified.

        Once called with a MIB module name, *compile* will:

        * fetch ASN.1 MIB module with given name by calling *sources*
        * make sure no such transformed MIB already exists (with *searchers*)
        * parse ASN.1 MIB text with *parser*
        * perform actual MIB transformation into target format with *code generator*
        * may attempt to borrow pre-transformed MIB through *borrowers*
        * write transformed MIB through *writer*

        Args:
            mibname: ASN.1 MIBs name
            options: options that affect the way PySMI components work

        Returns:
            A dictionary of MIB module names processed (keys) and *MibStatus*
            class instances (values)

        """
        processed = {}

        for source in self._sources:

            debug.logger & debug.flagCompiler and debug.logger('trying source %s' % source)

            try:
                fileInfo, fileData = source.getData(mibname)

                processed.update(
                    self._compileFileContents((fileInfo, fileData), context, depth, **options)
                )

                return processed

            except error.PySmiReaderFileNotFoundError:
                debug.logger & debug.flagCompiler and debug.logger('no %s found at %s' % (mibname, source))

            except error.PySmiError:
                exc_class, exc, tb = sys.exc_info()
                exc.source = source
                exc.mibname = mibname
                exc.msg += ' at MIB %s' % mibname

                debug.logger & debug.flagCompiler and debug.logger('%serror %s from %s' % (
                    options.get('ignoreErrors') and 'ignoring ' or 'failing on ', exc, source))

                processed[mibname] = statusFailed.setOptions(error=exc)

        exc = error.PySmiError('MIB source %s not found' % mibname)
        exc.mibname = mibname
        debug.logger & debug.flagCompiler and debug.logger('no %s found everywhere' % mibname)

        if mibname not in processed:
            processed[mibname] = statusMissing

        return processed

    def compileNext(self, *mibSources, **options):
        """Read MIBs one-by-one, transform read MIB and (optionally) its dependencies.

        Args:
            mibSources: list of reader objects to read MIBs from
            options: options that affect the way PySMI components work

        Returns:
            A generator which, when called, returns a dictionary of MIB module names
            just processed (keys) and *MibStatus* class instances (values)

        """
        mibDataGenerator = itertools.chain(
            *[source.dataGenerator() for source in mibSources]
        )

        context = {}

        for fileContents in mibDataGenerator:
            yield self._compileFileContents(fileContents, context, **options)

    def compile(self, *mibnames, **options):
        """Transform requested and, optionally, dependencies MIBs.

        The *compile* method should be invoked when *MibCompiler* object
        is operational meaning at least *sources* are specified.

        Once called with a MIB module name, *compile* will:

        * fetch ASN.1 MIB module with given name by calling *sources*
        * make sure no such transformed MIB already exists (with *searchers*)
        * parse ASN.1 MIB text with *parser*
        * perform actual MIB transformation into target format with *code generator*
        * may attempt to borrow pre-transformed MIB through *borrowers*
        * write transformed MIB through *writer*

        The above sequence will be performed for each MIB name given in
        *mibnames* and may be performed for all MIBs referred to from
        MIBs being processed.

        Args:
            mibnames: list of ASN.1 MIBs names
            options: options that affect the way PySMI components work

        Returns:
            A dictionary of MIB module names processed (keys) and *MibStatus*
            class instances (values)

        """
        result = {}
        context = {}

        for mibname in mibnames:
            processed = self.compileOne(mibname, context, **options)

            result.update(processed)

            for mibname in tuple(processed):
                if processed[mibname] == statusFailed:
                    if options.get('ignoreErrors'):
                        processed[mibname] = statusUnprocessed
                    else:
                        return result

        return result

    def buildIndex(self, processedMibs, **options):
        comments = [
            'Produced by %s-%s at %s' % (packageName, packageVersion, time.asctime()),
            'On host %s platform %s version %s by user %s' % (
                hasattr(os, 'uname') and os.uname()[1] or '?', hasattr(os, 'uname') and os.uname()[0] or '?',
                hasattr(os, 'uname') and os.uname()[2] or '?', hasattr(os, 'getuid') and getpwuid(os.getuid())[0]) or '?',
            'Using Python version %s' % sys.version.split('\n')[0]
        ]
        try:
            self._writer.putData(
                self.indexFile,
                self._codegen.genIndex(
                    processedMibs,
                    comments=comments,
                    old_index_data=self._writer.getData(self.indexFile)
                ),
                dryRun=options.get('dryRun')
            )
        except error.PySmiError:
            exc_class, exc, tb = sys.exc_info()
            exc.msg += ' at MIB index %s' % self.indexFile

            debug.logger & debug.flagCompiler and debug.logger('error %s when building %s' % (exc, self.indexFile))

            if options.get('ignoreErrors'):
                return

            if hasattr(exc, 'with_traceback'):
                raise exc.with_traceback(tb)
            else:
                raise exc
