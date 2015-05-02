import sys
import time
try:
    import httplib
except ImportError:
    import http.client as httplib
from pysmi.reader.base import AbstractReader
from pysmi import error
from pysmi import debug

class HttpReader(AbstractReader):
    def __init__(self, host, port, locationTemplate, timeout=5, ssl=False):
        self._schema = ssl and 'https' or 'http'
        self._host = host
        self._port = port
        self._locationTemplate = locationTemplate
        self._timeout = timeout

    def __str__(self):
        return '%s{"http://%s:%s%s"}' % (self.__class__.__name__, self._host, self._port, self._locationTemplate)

    def getData(self, timestamp, mibname):
        headers = {
            'If-Modified-Since': time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(timestamp)),
            'Accept': 'text/plain'
        }
        if sys.version_info[:2] < (2, 5):
            conn = httplib.HTTPConnection(self._host, self._port)
        else:
            conn = httplib.HTTPConnection(self._host, self._port, timeout=self._timeout)

        debug.logger & debug.flagReader and debug.logger('looking for MIB %s that is newer than %s' % (mibname, time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(timestamp))))

        for mibfile in self.getMibVariants(mibname):
            location = self._locationTemplate.replace('<mib>', mibfile)
            debug.logger & debug.flagReader and debug.logger('trying to fetch MIB from %s://%s:%s%s' % (self._schema, self._host, self._port, location))
            try:
                conn.request('GET', location, '', headers)
                response = conn.getresponse()
            except Exception:
                debug.logger & debug.flagReader and debug.logger('failed to fetch MIB from %s://%s:%s%s: %s' % (self._schema, self._host, self._port, location, sys.exc_info()[1]))
                continue

            debug.logger & debug.flagReader and debug.logger('HTTP response %s' % response.status)

            if response.status == 304:
                raise error.PySmiSourceNotModifiedError('HTTP response was %s' % response.status, reader=self)
            if response.status == 200:
                try:
                    lastModified = time.mktime(time.strptime(response.getheader('Last-Modified'), "%a, %d %b %Y %H:%M:%S %Z"))
                except:
                    debug.logger & debug.flagReader and debug.logger('malformed HTTP headers')
                    lastModified = 0
                if lastModified > timestamp:
                    debug.logger & debug.flagReader and debug.logger('source MIB %s is new enough (%s), fetching data...' % (response.getheader('Last-Modified'), location))
                    return response.read(self.maxMibSize).decode('utf-8', 'ignore')
                else:
                    raise error.PySmiSourceNotModifiedError('source MIB %s is older than needed' % location, reader=self)

        raise error.PySmiSourceNotFoundError('source MIB %s not found' % mibname, reader=self)
