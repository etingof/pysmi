#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pysmi.sf.net/license.html
#
import os
import sys
import time
import datetime
import zipfile
from pysmi.reader.base import AbstractReader
from pysmi.mibinfo import MibInfo
from pysmi.compat import decode
from pysmi import debug
from pysmi import error


class ZipReader(AbstractReader):
    """Fetch ASN.1 MIB text by name from local file.

    *FileReader* class instance tries to locate ASN.1 MIB files
    by name, fetch and return their contents to caller.
    """
    useIndexFile = True  # optional .index file mapping MIB to file name
    indexFile = '.index'

    def __init__(self, zipPath, ignoreErrors=True):
        """Create an instance of *FileReader* serving a directory.

           Args:
               archive (str): ZIP archive to search MIB files in
        """
        self._zipPath = zipPath
        self._ignoreErrors = ignoreErrors
        self._indexLoaded = False
        self._mibIndex = None
        self._archive = None
        self._members = None

    def __str__(self):
        return '%s{"%s"}' % (self.__class__.__name__, self._zipPath)

    @staticmethod
    def loadIndex(indexFile):
        mibIndex = {}
        if os.path.exists(indexFile):
            try:
                f = open(indexFile)
                mibIndex = dict(
                    [x.split()[:2] for x in f.readlines()]
                )
                f.close()
                debug.logger & debug.flagReader and debug.logger(
                    'loaded MIB index map from %s file, %s entries' % (indexFile, len(mibIndex)))

            except IOError:
                pass

        return mibIndex

    def getData(self, mibname):
        debug.logger & debug.flagReader and debug.logger(
            'looking for MIB %s at %s' % (mibname, self._zipPath))

        if self._archive is None:
            try:
                self._archive = zipfile.ZipFile(self._zipPath)
                self._members = dict(((os.path.basename(z.filename), z) for z in self._archive.infolist()))

            except Exception:
                raise error.PySmiError('ZIP archive %s access error: %s' % (self._zipPath, sys.exc_info()[1]))

        for mibalias, mibfile in self.getMibVariants(mibname):

            debug.logger & debug.flagReader and debug.logger('trying MIB %s' % mibfile)

            try:
                member = self._members[mibfile]

            except KeyError:
                continue

            try:
                mtime = time.mktime(datetime.datetime(*member.date_time[:6]).timetuple())

                debug.logger & debug.flagReader and debug.logger(
                    'source MIB %s mtime is %s, fetching data...' % (
                        f, time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(mtime))))

                fp = self._archive.open(member.filename)
                mibData = fp.read(self.maxMibSize)
                fp.close()

                if len(mibData) == self.maxMibSize:
                    raise IOError('MIB %s too large' % f)

                return MibInfo(path='zip://%s/%s' % (self._zipPath, member.filename),
                               file=mibfile, name=mibalias, mtime=mtime), decode(mibData)

            except (OSError, IOError):
                debug.logger & debug.flagReader and debug.logger(
                    'source file %s open failure: %s' % (member.filename, sys.exc_info()[1]))

                if not self._ignoreErrors:
                    raise error.PySmiError('file %s access error: %s' % (f, sys.exc_info()[1]))

                raise error.PySmiReaderFileNotModifiedError('source MIB %s is older than needed' % f, reader=self)

        raise error.PySmiReaderFileNotFoundError('source MIB %s not found' % mibname, reader=self)
