#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2019, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysmi/license.html
#


def capfirst(text):
    if not text:
        return text

    return text[0].upper() + text[1:]
