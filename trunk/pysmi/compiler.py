import sys
import os
import time
try:
    from pwd import getpwuid
except ImportError:
    getpwuid = lambda x: ['<unknown>']
from pysmi import __name__ as packageName
from pysmi import __version__ as packageVersion
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
        processed = {}
        related = set()
        for mibname in mibnames:
            debug.logger & debug.flagCompiler and debug.logger('checking %s for an update' % mibname)
            timeStamp = 0
            try:
                for searcher in self._searchers:
                    debug.logger & debug.flagCompiler and debug.logger('checking compiled files using %s' % searcher)
                    try:
                        timeStamp = max(timeStamp, searcher.getTimestamp(mibname, rebuild=kwargs.get('rebuild')))
                    except error.PySmiCompiledFileNotFoundError:
                        pass

            except error.PySmiCompiledFileTakesPrecedenceError:
                debug.logger & debug.flagCompiler and debug.logger('always use compiled file for %s' % mibname)
                processed[mibname] = statusUntouched
                continue

            debug.logger & debug.flagCompiler and debug.logger('done searching compiled versions of %s, %s' % (mibname, timeStamp and 'one or more found' or 'nothing found'))

            pendingError = None

            for source in self._sources:
                debug.logger & debug.flagCompiler and debug.logger('trying source %s' % source)
                comments = [
                    'Produced by %s-%s from %s at %s' % (packageName, packageVersion, mibname, time.asctime()),
                    'On host %s platform %s version %s by user %s' % (os.uname()[1], os.uname()[0], os.uname()[2], getpwuid(os.getuid())[0]),
                    'Using Python version %s' % sys.version.split('\n')[0]
                ]
                try:
                    fileInfo, fileData = source.getData(timeStamp, mibname)
                    mibInfo, mibData = self._codegen.genCode(
                        self._parser.__class__().parse(fileData), # XXX
                        comments=comments,
                        genTexts=kwargs.get('genTexts'),
                    )
                    self._writer.putData(
                        mibInfo.alias, mibData, dryRun=kwargs.get('dryRun')
                    )
                    processed[mibInfo.alias] = statusCompiled.setOptions(
                        alias=mibname, mibfile=fileInfo.mibfile, oid=mibInfo.oid
                    )
                    if fileInfo.alias != mibInfo.alias:
                        comments = [
'This is a stub pysnmp (http://pysnmp.sf.net) MIB file for %s' % mibInfo.alias,
'The sole purpose of this stub file is to keep track of',
'%s\'s modification time compared to MIB source' % fileInfo.alias,
'file %s' % fileInfo.mibfile
                        ]
                        self._writer.putData(
                            fileInfo.alias, '',
                            comments=comments,
                            dryRun=kwargs.get('dryRun')
                        )
                        processed[fileInfo.alias] = statusCompiled.setOptions(
                            alias=mibInfo.alias, mibfile=fileInfo.mibfile
                        )
                    debug.logger & debug.flagCompiler and debug.logger('%s (%s/%s) read from %s and compiled by %s immediate dependencies: %s' % (mibInfo.alias, mibname, fileInfo.alias, fileInfo.mibfile, self._writer, ', '.join(mibInfo.otherMibs) or '<none>'))
                    if kwargs.get('noDeps'):
                        for x in mibInfo.otherMibs:
                            processed[x] = statusUnprocessed
                    else:
                        related.update(mibInfo.otherMibs)
                    break
                except error.PySmiSourceNotModifiedError:
                    debug.logger & debug.flagCompiler and debug.logger('no update required for %s' % mibname)
                    processed[mibname] = statusUntouched
                    break
                except error.PySmiSourceNotFoundError:
                    debug.logger & debug.flagCompiler and debug.logger('no %s found at %s' % (mibname, source))
                    processed[mibname] = statusMissing
                    continue
                except error.PySmiError:
                    exc_class, exc, tb = sys.exc_info()
                    exc.source = source
                    exc.mibname = mibname
                    exc.timestamp = timeStamp
                    exc.message += ' at MIB %s' % mibname
                    debug.logger & debug.flagCompiler and debug.logger('%serror %s from %s' % (kwargs.get('ignoreErrors') and 'ignoring ' or 'failing on ', exc, source))
                    processed[mibname] = statusFailed.setOptions(exception=exc)
                    if self._borrowers:
                        debug.logger & debug.flagCompiler and debug.logger('will try borrowing failed MIB %s' % mibname)
                        pendingError = exc
                        continue
                    if kwargs.get('ignoreErrors'):
                        break
                    if hasattr(exc, 'with_traceback'):
                        raise exc.with_traceback(tb)
                    else:
                        raise exc
            else:
                for borrower in self._borrowers:
                    debug.logger & debug.flagCompiler and debug.logger('trying to borrow %s from %s' % (mibname, borrower))
                    try:
                        fileInfo, fileData = borrower.getData(
                            timeStamp,
                            mibname,
                            genTexts=kwargs.get('genTexts')
                        )
                        self._writer.putData(
                            fileInfo.alias,
                            fileData,
                            dryRun=kwargs.get('dryRun')
                        )
                        processed[mibname] = statusBorrowed.setOptions(alias=fileInfo.alias)
                        processed[fileInfo.alias] = statusBorrowed.setOptions(alias=mibname)
                        debug.logger & debug.flagCompiler and debug.logger('%s (%s) borrowed by %s' % (mibname, fileInfo.alias, self._writer))
                        break
                    except error.PySmiSourceNotModifiedError:
                        debug.logger & debug.flagCompiler and debug.logger('no borrowing required for %s' % mibname)
                        processed[mibname] = statusUntouched
                        break
                    except error.PySmiSourceNotFoundError:
                        debug.logger & debug.flagCompiler and debug.logger('no %s found at %s' % (mibname, borrower))
                        continue
                    except error.PySmiError:
                        exc_class, exc, tb = sys.exc_info()
                        exc.message += ' at MIB %s' % mibname
                        debug.logger & debug.flagCompiler and debug.logger('error %s from %s' % (exc, borrower))
                        continue
                else:
                    debug.logger & debug.flagCompiler and debug.logger('no more borrowers to try')
                    if kwargs.get('ignoreErrors'):
                        continue

                    if pendingError:
                        if hasattr(pendingError, 'with_traceback'):
                            raise pendingError.with_traceback(tb)
                        else:
                            raise pendingError
                            
                    if not timeStamp:
                        raise error.PySmiSourceNotFoundError('source MIB %s not found%s' % (mibname, mibname in processed and hasattr(processed[mibname], 'message') and ': (%s)' % processed[mibname].message or ''), mibname=mibname, timestamp=timeStamp)

        if related:
            debug.logger & debug.flagCompiler and debug.logger('compiling related MIBs: %s' % ', '.join(related))
            processed.update(self.compile(*related, **kwargs), **processed.copy())

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
            exc.message += ' at MIB index %s' % self.indexFile
            debug.logger & debug.flagCompiler and debug.logger('error %s when building %s' % (exc, self.indexFile))
            if kwargs.get('ignoreErrors'):
                return
            if hasattr(exc, 'with_traceback'):
                raise exc.with_traceback(tb)
            else:
                raise exc
