import os
import sys
import time
import imp
import py_compile
from pysmi.writer.base import AbstractWriter
from pysmi import debug
from pysmi import error

class PyFileWriter(AbstractWriter):
    suffixes = {}
    for sfx, mode, typ in imp.get_suffixes():
        if typ not in suffixes:
            suffixes[typ] = []
        suffixes[typ].append((sfx, mode))

    def __init__(self, path):
        self._path = os.path.normpath(path)

    def __str__(self): return '%s{"%s"}' % (self.__class__.__name__, self._path)

    def putData(self, mibname, data, alias='', dryRun=False):
        if dryRun:
            debug.logger & debug.flagWriter and debug.logger('dry run mode')
            return
        if not os.path.exists(self._path):
            try:
                os.makedirs(self._path)
            except OSError:
                raise error.PySmiWriterError('failure creating destination directory %s: %s' % (self._path, sys.exc_info()[1]), writer=self)

        pyfile = os.path.join(self._path, mibname) + self.suffixes[imp.PY_SOURCE][0][0]
        try:
            f = open(pyfile, 'wb')
            f.write(data.encode('utf-8'))
            f.close()
        except (IOError, UnicodeEncodeError):
            raise error.PySmiWriterError('failure writing file %s: %s' % (pyfile, sys.exc_info()[1]), file=pyfile, writer=self)

        debug.logger & debug.flagWriter and debug.logger('created file %s' % pyfile)

        if alias:
            pyalias = os.path.join(self._path, alias) + self.suffixes[imp.PY_SOURCE][0][0]
            try:
                os.unlink(pyalias)
                os.link(pyfile, pyalias)
            except (AttributeError, OSError):  # not all platforms support it
                try:
                    f = open(pyalias, 'wb')
                    f.write(data.encode('utf-8'))
                    f.close()
                except (IOError, UnicodeEncodeError):
                    raise error.PySmiWriterError('failure writing file %s: %s' % (pyalias, sys.exc_info()[1]), file=pyalias, alias=true, writer=self)
                else:
                    debug.logger & debug.flagWriter and debug.logger('a copy of file %s created as %s' % (pyfile, pyalias))
            else:
                debug.logger & debug.flagWriter and debug.logger('file %s linked to %s' % (pyalias, pyfile))
        
        for filename in mibname, alias:
            if not filename:
                continue
            try:
                py_compile.compile(pyfile, doraise=True)
            except (SyntaxError, py_compile.PyCompileError):
                pass  # XXX
            except:
                try:
                    os.unlink(pyfile)
                except:
                    pass
                raise error.PySmiWriterError('failure compiling %s: %s' % (filename, sys.exc_info()[1]), file=filename, writer=self)

            debug.logger & debug.flagWriter and debug.logger('compiled %s' % filename)

if __name__ == '__main__':
    from pysmi import debug

    debug.setLogger(debug.Debug('all'))

    f = PyFileWriter('/tmp/x')

    f.putData('X', 'print(123)')
