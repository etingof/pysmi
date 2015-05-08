import sys

if sys.version_info[0] > 2:
    def encode(s):
        if isinstance(s, str):
            s = s.encode('utf-8', 'ignore')
        return s

    def decode(s):
        if isinstance(s, bytes):
            s = s.decode('utf-8', 'ignore')
        return s
else:
    def encode(s):
        if isinstance(s, unicode):
            s = s.encode('utf-8', 'ignore')
        return s

    def decode(s):
        if isinstance(s, str):
            s = s.decode('utf-8', 'ignore')
        return s
