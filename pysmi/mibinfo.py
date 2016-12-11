#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2016, Ilya Etingof <ilya@glas.net>
# License: http://pysmi.sf.net/license.html
#

#
# Known attributes:
# name   -- actual MIB name
# alias  -- possible alternative to MIB name
# path   -- URL to MIB file
# file   -- MIB file name
# mtime  -- MIB file modification time
# oid    -- module OID
# identity -- MODULE-IDENTITY OID
# first  -- first OID defined in module
# last   -- last OID defined in module
# compliance -- list of MODULE-COMPLIANCE OIDs


class MibInfo(object):
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])
