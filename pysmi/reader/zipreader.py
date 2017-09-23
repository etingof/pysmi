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


class FileLike(object):
    """Stripped down, binary file mock to work with ZipFile"""
    def __init__(self, buf, name):
        self.name = name
        self.buf = buf
        self.null = buf[:0]
        self.len = len(buf)
        self.buflist = []
        self.pos = 0
        self.closed = False
        self.softspace = 0

    def close(self):
        if not self.closed:
            self.closed = True
            self.buf = self.null
            self.pos = 0

    def seek(self, pos, mode = 0):
        if self.buflist:
            self.buf += self.null.join(self.buflist)
            self.buflist = []

        if mode == 1:
            pos += self.pos

        elif mode == 2:
            pos += self.len

        self.pos = max(0, pos)

    def tell(self):
        return self.pos

    def read(self, n=-1):
        if self.buflist:
            self.buf += self.null.join(self.buflist)
            self.buflist = []

        if n < 0:
            newpos = self.len
        else:
            newpos = min(self.pos + n, self.len)

        r = self.buf[self.pos:newpos]

        self.pos = newpos

        return r


class ZipReader(AbstractReader):
    """Fetch ASN.1 MIB text by name from a ZIP archive.

    *ZipReader* class instance tries to locate ASN.1 MIB files
    by name, fetch and return their contents to caller.
    """
    useIndexFile = False

    def __init__(self, name):
        self._name = name
        self._members = None

    @property
    def members(self):
        if self._members is None:
            try:
                self._members = self._readZipDirectory(fileObj=open(self._name, 'rb'))

            except Exception:
                debug.logger & debug.flagReader and debug.logger(
                    'ZIP file %s open failure: %s' % (self._name, sys.exc_info()[1]))

                if not self.ignoreErrors:
                    raise error.PySmiError('file %s access error: %s' % (self._name, sys.exc_info()[1]))

                self._members = {}

        return self._members

    def _readZipDirectory(self, fileObj):

        archive = zipfile.ZipFile(fileObj)

        if isinstance(fileObj, FileLike):
            fileObj = None

        members = {}

        for member in archive.infolist():

            filename = os.path.basename(member.filename)
            if not filename:
                continue

            if (member.filename.endswith('.zip') or
                    member.filename.endswith('.ZIP')):

                innerZipBlob = archive.read(member.filename)

                innerMembers = self._readZipDirectory(FileLike(innerZipBlob, member.filename))

                for innerFilename, ref in innerMembers.items():

                    while innerFilename in members:
                        innerFilename += '+'

                    members[innerFilename] = [[fileObj, member.filename, None]]
                    members[innerFilename].extend(ref)

            else:
                mtime = time.mktime(datetime.datetime(*member.date_time[:6]).timetuple())

                members[filename] = [[fileObj, member.filename, mtime]]

        return members

    def _readZipFile(self, refs):

        for fileObj, filename, mtime in refs:

            if not fileObj:
                fileObj = FileLike(dataObj, name=self._name)

            archive = zipfile.ZipFile(fileObj)

            try:
                dataObj = archive.read(filename)

            except Exception:
                debug.logger & debug.flagReader and debug.logger('ZIP read component %s read error: %s' % (fileObj.name, sys.exc_info()[1]))
                return '', 0

        return dataObj, mtime

    def __str__(self):
        return '%s{"%s"}' % (self.__class__.__name__, self._name)

    def getData(self, mibname):
        debug.logger & debug.flagReader and debug.logger('looking for MIB %s at %s' % (mibname, self._name))

        if not self.members:
            raise error.PySmiReaderFileNotFoundError('source MIB %s not found' % mibname, reader=self)

        for mibalias, mibfile in self.getMibVariants(mibname):

            debug.logger & debug.flagReader and debug.logger('trying MIB %s' % mibfile)

            try:
                refs = self.members[mibfile]

            except KeyError:
                continue

            mibData, mtime = self._readZipFile(refs)

            if not mibData:
                continue

            debug.logger & debug.flagReader and debug.logger(
                'source MIB %s, mtime %s, read from %s/%s' % (mibfile, time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(mtime)), self._name, mibfile)
            )

            if len(mibData) == self.maxMibSize:
                raise IOError('MIB %s/%s too large' % (self._name, mibfile))

            return MibInfo(path='zip://%s/%s' % (self._name, mibfile),
                           file=mibfile, name=mibalias, mtime=mtime), decode(mibData)

        raise error.PySmiReaderFileNotFoundError('source MIB %s not found' % mibname, reader=self)

    def dataGenerator(self):
        debug.logger & debug.flagReader and debug.logger(
            'iterating over MIB source %s' % self)

        for mibfile in self.members:

            refs = self.members[mibfile]

            mibData, mtime = self._readZipFile(refs)

            if not mibData:
                continue

            debug.logger & debug.flagReader and debug.logger(
                'source MIB %s, mtime %s, read from %s/%s' % (
                mibfile, time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(mtime)), self._name, mibfile)
            )

            if len(mibData) == self.maxMibSize:
                raise IOError('MIB %s/%s too large' % (self._name, mibfile))

            yield MibInfo(path='zip://%s/%s' % (self._name, mibfile),
                          file=mibfile, name=mibfile, mtime=mtime), decode(mibData)
