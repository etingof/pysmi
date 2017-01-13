#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pysmi.sf.net/license.html
#


class AbstractParser(object):
    def reset(self):
        raise NotImplementedError()

    def parse(self, data, **kwargs):
        raise NotImplementedError()
