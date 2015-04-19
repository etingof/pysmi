import sys
from pysmi import error
from pysmi import debug


class MibCompiler(object):
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
        processed = set()
        unprocessed = set()
        for mibname in mibnames:
            debug.logger & debug.flagCompiler and debug.logger('checking %s for an update' % mibname)
            timeStamp = 0
            for compiled in self._compiled:
                debug.logger & debug.flagCompiler and debug.logger('checking compiled files using %s' % compiled)
                try:
                    timeStamp = max(timeStamp, compiled.getTimestamp(mibname, rebuild=kwargs.get('rebuild')))
                except error.PySmiCompiledFileNotFoundError:
                    pass

            debug.logger & debug.flagCompiler and debug.logger('done searching compiled versions of %s, %s' % (mibname, timeStamp and 'one or more found' or 'nothing found'))

            for source in self._sources:
                debug.logger & debug.flagCompiler and debug.logger('trying source %s' % source)
                try:
                    thismib, othermibs, data = self._codegen.genCode(
                        self._parser.parse(
                            source.getData(timeStamp, mibname)
                        ),
                        genTexts=kwargs.get('genTexts')
                    )
                    self._writer.putData(
                        thismib, data,
                        alias=mibname != thismib and mibname or '',
                        dryRun=kwargs.get('dryRun')
                    )
                    processed.add(thismib)
                    debug.logger & debug.flagCompiler and debug.logger('%s (%s) compiled by %s%s' % (thismib, mibname, self._writer, othermibs and 'checking dependencies' or ' '))
                    if not kwargs.get('noDeps'):
                        unprocessed.update(othermibs)
                    break
                except error.PySmiSourceNotModifiedError:
                    debug.logger & debug.flagCompiler and debug.logger('no update required for %s' % mibname)
                    break
                except error.PySmiSourceNotFoundError:
                    debug.logger & debug.flagCompiler and debug.logger('no %s found at %s' % (mibname, source))
                    continue
                except error.PySmiError:
                    exc_class, exc, tb = sys.exc_info()
                    exc.source = source
                    exc.mibname = mibname
                    exc.timestamp = timeStamp
                    exc.message += ' at MIB %s' % mibname
                    debug.logger & debug.flagCompiler and debug.logger('error %s from %s' % (exc, source))
                    if hasattr(exc, 'with_traceback'):
                        raise exc.with_traceback(tb)
                    else:
                        raise exc
            else:
                if not timeStamp:
                    raise error.PySmiSourceNotFoundError('source MIB %s not found' % mibname, mibname=mibname, timestamp=timeStamp)

        if unprocessed:
            debug.logger & debug.flagCompiler and debug.logger('compiling related MIBs: %s' % ', '.join(unprocessed))
            processed.update(self.compile(*unprocessed, **kwargs))

        return processed

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
