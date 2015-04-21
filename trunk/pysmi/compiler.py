import sys
import os
import time
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

class MibCompiler(object):
    indexFile = 'index'
    def __init__(self, parser, codegen, writer):
        self._parser = parser
        self._codegen = codegen
        self._writer = writer
        self._sources = []
        self._compiled = []

    def addSources(self, *sources):
        self._sources.extend(sources)
        debug.logger & debug.flagCompiler and debug.logger('current MIB source(s): %s' % ', '.join([str(x) for x in self._sources]))
        return self

    def addSearchers(self, *compiled):
        self._compiled.extend(compiled)
        debug.logger & debug.flagCompiler and debug.logger('current compiled MIBs location(s): %s' % ', '.join([str(x) for x in self._compiled]))
        return self

    def compile(self, *mibnames, **kwargs):
        processed = {}
        related = set()
        for mibname in mibnames:
            debug.logger & debug.flagCompiler and debug.logger('checking %s for an update' % mibname)
            timeStamp = 0
            try:
                for compiled in self._compiled:
                    debug.logger & debug.flagCompiler and debug.logger('checking compiled files using %s' % compiled)
                    try:
                        timeStamp = max(timeStamp, compiled.getTimestamp(mibname, rebuild=kwargs.get('rebuild')))
                    except error.PySmiCompiledFileNotFoundError:
                        pass

            except error.PySmiCompiledFileTakesPrecedenceError:
                debug.logger & debug.flagCompiler and debug.logger('always use compiled file for %s' % mibname)
                processed[mibname] = statusUntouched
                continue

            debug.logger & debug.flagCompiler and debug.logger('done searching compiled versions of %s, %s' % (mibname, timeStamp and 'one or more found' or 'nothing found'))

            for source in self._sources:
                debug.logger & debug.flagCompiler and debug.logger('trying source %s' % source)
                comments = [
                    'Produced by %s-%s from %s at %s' % (packageName, packageVersion, mibname, time.asctime()),
                    'On host %s platform %s version %s by user %s' % (os.uname()[1], os.uname()[0], os.uname()[2], os.getlogin()),
                    'Using Python version %s' % sys.version.split('\n')[0]
                ]
                try:
                    thismib, mibOid, othermibs, data = self._codegen.genCode(
                        self._parser.__class__().parse(
                            source.getData(timeStamp, mibname)
                        ),
                        genTexts=kwargs.get('genTexts'),
                        comments=comments
                    )
                    self._writer.putData(
                        thismib, data,
                        alias=mibname != thismib and mibname or '',
                        dryRun=kwargs.get('dryRun')
                    )
                    processed[thismib] = statusCompiled.setOptions(
                        alias=mibname, oid=mibOid
                    )
                    processed[mibname] = statusCompiled.setOptions(
                        alias=thismib
                    )
                    debug.logger & debug.flagCompiler and debug.logger('%s (%s) compiled by %s immediate dependencies: %s' % (thismib, mibname, self._writer, ', '.join(othermibs) or '<none>'))
                    if kwargs.get('noDeps'):
                        for x in othermibs:
                            processed[x] = statusUnprocessed
                    else:
                        related.update(othermibs)
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
                    debug.logger & debug.flagCompiler and debug.logger('error %s from %s' % (exc, source))
                    processed[mibname] = statusFailed.setOptions(exception=exc)
                    if kwargs.get('ignoreErrors'):
                        break
                    if hasattr(exc, 'with_traceback'):
                        raise exc.with_traceback(tb)
                    else:
                        raise exc
            else:
                if kwargs.get('ignoreErrors'):
                    continue
                if not timeStamp:
                    raise error.PySmiSourceNotFoundError('source MIB %s not found' % mibname, mibname=mibname, timestamp=timeStamp)

        if related:
            debug.logger & debug.flagCompiler and debug.logger('compiling related MIBs: %s' % ', '.join(related))
            processed.update(self.compile(*related, **kwargs))

        return processed

    def buildIndex(self, processedMibs, **kwargs):
        comments = [
            'Produced by %s-%s at %s' % (packageName, packageVersion, time.asctime()),
            'On host %s platform %s version %s by user %s' % (os.uname()[1], os.uname()[0], os.uname()[2], os.getlogin()),
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

if __name__ == '__main__':
    from pysmi.reader.localfile import FileReader
    from pysmi.searcher.pyfile import PyFileSearcher
    from pysmi.searcher.pypackage import PyPackageSearcher
    from pysmi.searcher.stub import StubSearcher
    from pysmi.writer.pyfile import PyFileWriter
    from pysmi.parser.smiv2 import SmiV2Parser
    from pysmi import debug

    debug.setLogger(debug.Debug('all'))

    s = MibCompiler(SmiV2Parser(), PyFileWriter('/tmp/x'))

    s.addSources(FileReader('/usr/share/snmp/mibs'))

    s.addSearchers(
        StubSearcher('SNMPv2-SMI',
                     'SNMPv2-TC',
                     'SNMPv2-CONF',
                     'SNMPv2-MIB'),
        PyPackageSearcher('pysnmp.smi.mibs'),
        PyPackageSearcher('pysnmp_mibs'),
        PyFileSearcher('/tmp/x')
    )

    s.compile('IF-MIB')
