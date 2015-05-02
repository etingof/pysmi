import sys
import time
import ftplib
from pysmi.reader.base import AbstractReader
from pysmi import error
from pysmi import debug

class FtpReader(AbstractReader):
    def __init__(self, host, locationTemplate, timeout=5, ssl=False, port=21,
                 user='anonymous', password='anonymous@'):
        self._host = host
        self._locationTemplate = locationTemplate
        self._timeout = timeout
        self._ssl = ssl
        self._port = port
        self._user = user
        self._password = password

    def __str__(self):
        return '%s{"ftp://%s%s"}' % (self.__class__.__name__, self._host, self._locationTemplate)

    def getData(self, timestamp, mibname):
        if self._ssl:
            conn = ftplib.FTP_TLS()
        else:
            conn = ftplib.FTP()

        try:
            conn.connect(self._host, self._port, self._timeout)
        except ftplib.all_errors:
            raise error.PySmiSourceNotFoundError('failed to connect to FTP server %s:%s: %s' % (self._host, self._port, sys.exc_info()[1]), reader=self)

        try:
            conn.login(self._user, self._password)
        except ftplib.all_errors:
            conn.close()
            raise error.PySmiSourceNotFoundError('failed to log in to FTP server %s:%s as %s/%s: %s' % (self._host, self._port, self._user, self._password, sys.exc_info()[1]), reader=self)

        debug.logger & debug.flagReader and debug.logger('looking for MIB %s that is newer than %s' % (mibname, time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(timestamp))))

        for mibfile in self.getMibVariants(mibname):
            location = self._locationTemplate.replace('<mib>', mibfile)
            debug.logger & debug.flagReader and debug.logger('trying to fetch MIB %s from %s:%s' % (location, self._host, self._port))
            data = []
            try:
                try:
                    response = conn.sendcmd('MDTM %s' % location)
                except ftplib.all_errors:
                    debug.logger & debug.flagReader and debug.logger('server %s:%s does not support MDTM command, fetching file %s' % (self._host, self._port, location))
                    lastModified = timestamp+1
                else:
                    debug.logger & debug.flagReader and debug.logger('server %s:%s MDTM response is %s' % (self._host, self._port, response))
                    if response[:3] == 213:
                        lastModified = time.mktime(time.strptime(response[4:], "%Y%m%d%H%M%S"))
                    else:
                        lastModified = timestamp+1

                if lastModified > timestamp:
                    debug.logger & debug.flagReader and debug.logger('source MIB %s is new enough (%s), fetching data...' % (location, time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(lastModified))))
                    conn.retrlines('RETR %s' % location, lambda x, y=data: y.append(x))
                else:
                    conn.close()
                    raise error.PySmiSourceNotModifiedError('source MIB %s is older than needed' % location, reader=self)

            except ftplib.all_errors:
                debug.logger & debug.flagReader and debug.logger('failed to fetch MIB %s from %s:%s: %s' % (location, self._host, self._port, sys.exc_info()[1]))
                continue

            data = '\n'.join(data)

            data = data.decode('utf-8', 'ignore')

            debug.logger & debug.flagReader and debug.logger('fetched %s bytes in %s' % (len(data), location))

            conn.close()
            return data

        conn.close()

        raise error.PySmiSourceNotFoundError('source MIB %s not found' % mibname, reader=self)
