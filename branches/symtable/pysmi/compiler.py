import sys
import os
import time
try:
    from pwd import getpwuid
except ImportError:
    getpwuid = lambda x: ['<unknown>']
from pysmi import __name__ as packageName
from pysmi import __version__ as packageVersion
from pysmi.codegen.symtable import SymtableCodeGen
from pysmi import error
from pysmi import debug

class MibStatus(str):
    def setOptions(self, **kwargs):
        n = self.__class__(self)
        for k in kwargs:
            setattr(n, k, kwargs[k])
        return n

statusCompiled = MibStatus('compiled')
statusUntouched = MibStatus('untouched')
statusFailed = MibStatus('failed')
statusUnprocessed = MibStatus('unprocessed')
statusMissing = MibStatus('missing')
statusBorrowed = MibStatus('borrowed')

class MibCompiler(object):
    indexFile = 'index'
    def __init__(self, parser, codegen, writer):
        self._parser = parser
        self._codegen = codegen
        self._symbolgen = SymtableCodeGen()
        self._writer = writer
        self._sources = []
        self._searchers = []
        self._borrowers = []

    def addSources(self, *sources):
        self._sources.extend(sources)
        debug.logger & debug.flagCompiler and debug.logger('current MIB source(s): %s' % ', '.join([str(x) for x in self._sources]))
        return self

    def addSearchers(self, *searchers):
        self._searchers.extend(searchers)
        debug.logger & debug.flagCompiler and debug.logger('current compiled MIBs location(s): %s' % ', '.join([str(x) for x in self._searchers]))
        return self

    def addBorrowers(self, *borrowers):
        self._borrowers.extend(borrowers)
        debug.logger & debug.flagCompiler and debug.logger('current MIB borrower(s): %s' % ', '.join([str(x) for x in self._borrowers]))
        return self

    def compile(self, *mibnames, **kwargs):
        #
        # Load and parse all requested and imported MIBs
        #
        parsedMibs = {}; failedMibs = {}; builtMibs = {}
        mibsToParse = [ x for x in mibnames ]
        while mibsToParse:
            mibname = mibsToParse.pop(0)
            if mibname in parsedMibs:
                debug.logger & debug.flagCompiler and debug.logger('MIB %s already parsed' % mibname)
                continue
            if mibname in failedMibs:
                debug.logger & debug.flagCompiler and debug.logger('MIB %s already failed' % mibname)
                continue

            for source in self._sources:
                debug.logger & debug.flagCompiler and debug.logger('trying source %s' % source)
                try:
                    fileInfo, fileData = source.getData(mibname)
                    for mibTree in self._parser.__class__().parse(fileData):
                        mibInfo, symbolTable = self._symbolgen.genCode(
                            mibTree, {}
                        )

                        parsedMibs[mibInfo.alias] = fileInfo, mibInfo, symbolTable, mibTree
                        # XXX
                        mibInfo.otherMibs = [ x for x in mibInfo.otherMibs if x[:3] != 'ASN' ]
                        mibsToParse.extend(mibInfo.otherMibs)

                        debug.logger & debug.flagCompiler and debug.logger('%s (%s) read from %s, immediate dependencies: %s' % (mibInfo.alias, mibname, fileInfo.mibfile, ', '.join(mibInfo.otherMibs) or '<none>'))

                    break

                except error.PySmiSourceNotFoundError:
                    debug.logger & debug.flagCompiler and debug.logger('no %s found at %s' % (mibname, source))
                    continue
                except error.PySmiError:
                    exc_class, exc, tb = sys.exc_info()
                    exc.source = source
                    exc.mibname = mibname
                    exc.msg += ' at MIB %s' % mibname
                    debug.logger & debug.flagCompiler and debug.logger('%serror %s from %s' % (kwargs.get('ignoreErrors') and 'ignoring ' or 'failing on ', exc, source))
                    failedMibs[mibname] = exc
            else:
                exc = error.PySmiError('MIB source %s not found' % mibname)
                exc.mibname = mibname
                debug.logger & debug.flagCompiler and debug.logger('no %s found everywhare' % mibname)
                failedMibs[mibname] = exc

        debug.logger & debug.flagCompiler and debug.logger('MIBs analized %s, MIBs failed %s' % (len(parsedMibs), len(failedMibs)))

        #
        # See what MIBs need generating
        #

        for mibname in parsedMibs.copy():
            fileInfo, mibInfo, symbolTable, mibTree = parsedMibs[mibname]
            debug.logger & debug.flagCompiler and debug.logger('checking if %s requires updating' % mibname)
            for searcher in self._searchers:
                try:
                    searcher.fileExists(mibname, fileInfo.mtime, rebuild=kwargs.get('rebuild'))
                except error.PySmiCompiledFileNotFoundError:
                    debug.logger & debug.flagCompiler and debug.logger('no compiled MIB %s available through %s' % (mibname, searcher))
                    continue

                except (error.PySmiSourceNotModifiedError,
                        error.PySmiCompiledFileTakesPrecedenceError):
                    debug.logger & debug.flagCompiler and debug.logger('will be using existing compiled MIB %s found by %s' % (mibname, searcher))
                    del parsedMibs[mibname]
                    break

                except error.PySmiError:
                    exc_class, exc, tb = sys.exc_info()
                    exc.searcher = searcher
                    exc.mibname = mibname
                    exc.msg += ' at MIB %s' % mibname
                    debug.logger & debug.flagCompiler and debug.logger('error %s from %s' % (exc, source))
                    failedMibs[mibname] = exc
                    del parsedMibs[mibname]
                    break
            else:
                debug.logger & debug.flagCompiler and debug.logger('no suitable compiled MIB %s found anywhere' % mibname)
        else:
            debug.logger & debug.flagCompiler and debug.logger('MIBs parsed %s, MIBs failed %s' % (len(parsedMibs), len(failedMibs)))

        #
        # Generate code for parsed MIBs
        #

        for mibname in parsedMibs.copy():
            fileInfo, mibInfo, symbolTable, mibTree = parsedMibs[mibname]

            comments = [
                'Produced by %s-%s from %s at %s' % (packageName, packageVersion, mibname, time.asctime()),
                'On host %s platform %s version %s by user %s' % (os.uname()[1], os.uname()[0], os.uname()[2], getpwuid(os.getuid())[0]),
                'Using Python version %s' % sys.version.split('\n')[0],
                'From source file %s' % fileInfo.mibfile
            ]

            try:
                mibInfo, mibData = self._codegen.genCode(
                        mibTree,
                        symbolTable,
                        comments=comments,
                        genTexts=kwargs.get('genTexts')
                    )

                builtMibs[mibname] = mibData

                debug.logger & debug.flagCompiler and debug.logger('%s read from %s and compiled by %s' % (mibname, fileInfo.mibfile, self._writer))

            except error.PySmiError:
                exc_class, exc, tb = sys.exc_info()
                exc.handler = self._codegen
                exc.mibname = mibname
                exc.msg += ' at MIB %s' % mibname
                debug.logger & debug.flagCompiler and debug.logger('error %s from %s' % (exc, self._codegen))
                failedMibs[mibname] = exc
                del parsedMibs[mibname]
        else:
            debug.logger & debug.flagCompiler and debug.logger('MIBs parsed %s, MIBs failed %s' % (len(parsedMibs), len(failedMibs)))

        #
        # Try to borrow pre-compiled MIBs for failed ones
        #

        for mibname in failedMibs.copy():
	    for borrower in self._borrowers:
		debug.logger & debug.flagCompiler and debug.logger('trying to borrow %s from %s' % (mibname, borrower))
		try:
		    fileInfo, fileData = borrower.getData(
			mibname,
			genTexts=kwargs.get('genTexts')
		    )

                    builtMibs[mibname] = fileData

                    del failedMibs[mibname]

                    debug.logger & debug.flagCompiler and debug.logger('%s borrowed with %s' % (mibname, borrower))

                except error.PySmiError:
                    debug.logger & debug.flagCompiler and debug.logger('error %s from %s' % (exc, self._codegen))
        else:
            debug.logger & debug.flagCompiler and debug.logger('MIBs parsed %s, MIBs failed %s' % (len(parsedMibs), len(failedMibs)))

        #
        # We could attempt to ignore missing/failed MIBs
        #

        if failedMibs and not kwargs.get('ignoreErrors'):
            debug.logger & debug.flagCompiler and debug.logger('failing with problem MIBs %s' % ', '.join(failedMibs))
            processed = {}
            for mibname in failedMibs:
                processed[mibname] = statusFailed.setOptions(
                    exception=failedMibs[mibname]
                )
            for mibname in parsedMibs:
                processed[mibname] = statusUnprocessed.setOptions(
                    exception=error.PySmiError('Ignore MIB due to other failures')
                )
            return processed

        debug.logger & debug.flagCompiler and debug.logger('proceeding with built MIBs %s, failed MIBs %s' % (', '.join(builtMibs), ', '.join(failedMibs)))

        #
        # Store compiled MIBs
        #

        for mibname in builtMibs.copy():
            try:
                self._writer.putData(
                    mibname, builtMibs[mibname], dryRun=kwargs.get('dryRun')
                )

                debug.logger & debug.flagCompiler and debug.logger('%s stored by %s' % (mibname, self._writer))

            except error.PySmiError:
                exc_class, exc, tb = sys.exc_info()
                exc.handler = self._codegen
                exc.mibname = mibname
                exc.msg += ' at MIB %s' % mibname
                debug.logger & debug.flagCompiler and debug.logger('error %s from %s' % (exc, self._writer))
                failedMibs[mibname] = exc
                del builtMibs[mibname]
        else:
            debug.logger & debug.flagCompiler and debug.logger('%s MIBs stored' % len(parsedMibs))

        processed = {}
        for mibname in failedMibs:
            processed[mibname] = statusFailed.setOptions(
                exception=failedMibs[mibname], alias=mibname
            )
        for mibname in builtMibs:
            processed[mibname] = statusCompiled.setOptions(
                alias=mibname
        )
        return processed

    def buildIndex(self, processedMibs, **kwargs):
        comments = [
            'Produced by %s-%s at %s' % (packageName, packageVersion, time.asctime()),
            'On host %s platform %s version %s by user %s' % (os.uname()[1], os.uname()[0], os.uname()[2], getpwuid(os.getuid())[0]),
            'Using Python version %s' % sys.version.split('\n')[0]
        ]
        try:
            self._writer.putData(
                self.indexFile,
                self._codegen.genIndex(
                    dict([(x, x.oid) for x in processedMibs if hasattr(x, 'oid')]),
                    comments=comments
                ),
                dryRun=kwargs.get('dryRun')
            )
        except error.PySmiError:
            exc_class, exc, tb = sys.exc_info()
            exc.msg += ' at MIB index %s' % self.indexFile
            debug.logger & debug.flagCompiler and debug.logger('error %s when building %s' % (exc, self.indexFile))
            if kwargs.get('ignoreErrors'):
                return
            if hasattr(exc, 'with_traceback'):
                raise exc.with_traceback(tb)
            else:
                raise exc
