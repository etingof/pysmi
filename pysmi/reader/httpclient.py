#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pysmi.sf.net/license.html
#
import sys
import time

try:
    # noinspection PyUnresolvedReferences
    import httplib
except ImportError:
    # noinspection PyUnresolvedReferences
    import http.client as httplib
from pysmi.reader.base import AbstractReader
from pysmi.mibinfo import MibInfo
from pysmi.compat import decode
from pysmi import error
from pysmi import debug


class HttpReader(AbstractReader):
    """Fetch ASN.1 MIB text by name from a web site.

        *HttpReader* class instance tries to download ASN.1 MIB files
        by name and return their contents to caller.
    """

    MIB_MAGIC = '@mib@'

    def __init__(self, host, port, locationTemplate, timeout=5, ssl=False):
        """Create an instance of *HttpReader* bound to specific URL.

           Args:
               host (str): domain name or IP address of web server
               port (int): TCP port web server is listening
               locationTemplate (str): location part of the URL containing @mib@ magic placeholder to be replaced with MIB name fetch.
           Keyword Args:
               timeout (int): response timeout
               ssl (bool): access HTTPS web site
        """
        self._schema = ssl and 'https' or 'http'
        self._host = host
        self._port = port
        self._locationTemplate = decode(locationTemplate)
        self._timeout = timeout

    def __str__(self):
        return '%s{"%s://%s:%s%s"}' % (
            self.__class__.__name__, self._schema, self._host, self._port, self._locationTemplate)

    def getData(self, mibname):
        headers = {
            'Accept': 'text/plain'
        }
        if sys.version_info[:2] < (2, 6):
            conn = httplib.HTTPConnection(self._host, self._port)
        else:
            conn = httplib.HTTPConnection(self._host, self._port, timeout=self._timeout)

        mibname = decode(mibname)

        debug.logger & debug.flagReader and debug.logger('looking for MIB %s' % mibname)

        for mibalias, mibfile in self.getMibVariants(mibname):
            if self.MIB_MAGIC in self._locationTemplate:
                location = self._locationTemplate.replace(self.MIB_MAGIC, mibfile)
            else:
                location = self._locationTemplate + mibfile

            debug.logger & debug.flagReader and debug.logger(
                'trying to fetch MIB from %s://%s:%s%s' % (self._schema, self._host, self._port, location))

            try:
                conn.request('GET', location, '', headers)
                response = conn.getresponse()

            except Exception:
                debug.logger & debug.flagReader and debug.logger('failed to fetch MIB from %s://%s:%s%s: %s' % (
                    self._schema, self._host, self._port, location, sys.exc_info()[1]))
                continue

            debug.logger & debug.flagReader and debug.logger('HTTP response %s' % response.status)

            if response.status == 200:
                try:
                    mtime = time.mktime(time.strptime(response.getheader('Last-Modified'), "%a, %d %b %Y %H:%M:%S %Z"))

                except Exception:
                    debug.logger & debug.flagReader and debug.logger('malformed HTTP headers: %s' % sys.exc_info()[1])
                    mtime = time.time()

                debug.logger & debug.flagReader and debug.logger(
                    'fetching source MIB %s, mtime %s' % (location, response.getheader('Last-Modified')))

                return MibInfo(path='%s://%s:%s%s' % (self._schema, self._host, self._port, location), file=mibfile,
                               name=mibalias, mtime=mtime), decode(response.read(self.maxMibSize))

        raise error.PySmiReaderFileNotFoundError('source MIB %s not found' % mibname, reader=self)
