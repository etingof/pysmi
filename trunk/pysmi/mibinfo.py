
# known attributes:
# mibname -- requested MIB name
# alias   -- actual MIB name
# mibfile -- full path to source MIB file
# oid     -- top-level OID defined in this MIB

class MibInfo(object):
    def __init__(self, **kwargs):
        for k in kwargs:
            setattr(self, k, kwargs[k])
