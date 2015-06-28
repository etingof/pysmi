import imp
from pysmi.borrower.base import AbstractBorrower

class PyFileBorrower(AbstractBorrower):
    """Transformed MIB modules borrower.
    """
    for sfx, mode, typ in imp.get_suffixes():
        if typ == imp.PY_SOURCE:
            exts = [ sfx ]
            break
