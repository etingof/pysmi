#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pysmi.sf.net/license.html
#
from pysmi.borrower.base import AbstractBorrower


class AnyFileBorrower(AbstractBorrower):
    """Transformed MIB modules borrower.
    """
