#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2017, Ilya Etingof <etingof@gmail.com>
# License: http://pysmi.sf.net/license.html
#
import sys
import os
import tempfile

try:
    import unittest2 as unittest

except ImportError:
    import unittest

try:
    import StringIO

except ImportError:
    from io import StringIO

from pysmi.reader import ZipReader


class ZipReaderTestCase(unittest.TestCase):

    zipArchive = [
        80, 75, 3, 4, 10, 0, 0, 0, 0, 0, 8, 135, 53, 75, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 5, 0, 28, 0, 116, 101, 115, 116, 47, 85, 84, 9, 0, 3, 16, 211, 195, 89,
        25, 211, 195, 89, 117, 120, 11, 0, 1, 4, 140, 102, 0, 0, 4, 140, 102, 0, 0, 80,
        75, 3, 4, 10, 0, 0, 0, 0, 0, 230, 134, 53, 75, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 12, 0, 28, 0, 116, 101, 115, 116, 47, 115, 117, 98, 100, 105, 114, 47,
        85, 84, 9, 0, 3, 207, 210, 195, 89, 3, 211, 195, 89, 117, 120, 11, 0, 1, 4,
        140, 102, 0, 0, 4, 140, 102, 0, 0, 80, 75, 3, 4, 10, 0, 0, 0, 0, 0, 230, 134,
        53, 75, 102, 214, 67, 99, 2, 0, 0, 0, 2, 0, 0, 0, 17, 0, 28, 0, 116, 101, 115,
        116, 47, 115, 117, 98, 100, 105, 114, 47, 116, 101, 115, 116, 65, 85, 84, 9,
        0, 3, 207, 210, 195, 89, 3, 211, 195, 89, 117, 120, 11, 0, 1, 4, 140, 102, 0,
        0, 4, 140, 102, 0, 0, 66, 10, 80, 75, 3, 4, 10, 0, 0, 0, 0, 0, 2, 135, 53, 75,
        162, 170, 2, 92, 138, 7, 0, 0, 138, 7, 0, 0, 13, 0, 28, 0, 116, 101, 115, 116,
        47, 116, 101, 115, 116, 46, 122, 105, 112, 85, 84, 9, 0, 3, 3, 211, 195, 89,
        3, 211, 195, 89, 117, 120, 11, 0, 1, 4, 140, 102, 0, 0, 4, 140, 102, 0, 0, 80,
        75, 3, 4, 10, 0, 0, 0, 0, 0, 253, 134, 53, 75, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 5, 0, 28, 0, 116, 101, 115, 116, 47, 85, 84, 9, 0, 3, 253, 210, 195, 89, 3,
        211, 195, 89, 117, 120, 11, 0, 1, 4, 140, 102, 0, 0, 4, 140, 102, 0, 0, 80, 75,
        3, 4, 10, 0, 0, 0, 0, 0, 230, 134, 53, 75, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        12, 0, 28, 0, 116, 101, 115, 116, 47, 115, 117, 98, 100, 105, 114, 47, 85, 84,
        9, 0, 3, 207, 210, 195, 89, 3, 211, 195, 89, 117, 120, 11, 0, 1, 4, 140, 102,
        0, 0, 4, 140, 102, 0, 0, 80, 75, 3, 4, 10, 0, 0, 0, 0, 0, 130, 131, 53, 75,
        227, 250, 30, 37, 12, 0, 0, 0, 12, 0, 0, 0, 21, 0, 28, 0, 116, 101, 115, 116,
        47, 115, 117, 98, 100, 105, 114, 47, 116, 101, 115, 116, 65, 46, 116, 120,
        116, 85, 84, 9, 0, 3, 116, 204, 195, 89, 134, 204, 195, 89, 117, 120, 11, 0,
        1, 4, 140, 102, 0, 0, 4, 140, 102, 0, 0, 115, 117, 98, 100, 105, 114, 116,
        101, 115, 116, 65, 10, 80, 75, 3, 4, 10, 0, 0, 0, 0, 0, 109, 131, 53, 75, 237,
        78, 102, 83, 6, 0, 0, 0, 6, 0, 0, 0, 14, 0, 28, 0, 116, 101, 115, 116, 47,
        116, 101, 115, 116, 65, 46, 116, 120, 116, 85, 84, 9, 0, 3, 78, 204, 195, 89,
        134, 204, 195, 89, 117, 120, 11, 0, 1, 4, 140, 102, 0, 0, 4, 140, 102, 0, 0,
        116, 101, 115, 116, 65, 10, 80, 75, 3, 4, 10, 0, 0, 0, 0, 0, 144, 131, 53,
        75, 204, 176, 61, 249, 144, 2, 0, 0, 144, 2, 0, 0, 13, 0, 28, 0, 116, 101,
        115, 116, 47, 116, 101, 115, 116, 46, 122, 105, 112, 85, 84, 9, 0, 3, 143,
        204, 195, 89, 143, 204, 195, 89, 117, 120, 11, 0, 1, 4, 140, 102, 0, 0, 4,
        140, 102, 0, 0, 80, 75, 3, 4, 10, 0, 0, 0, 0, 0, 117, 131, 53, 75, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 28, 0, 116, 101, 115, 116, 47, 85, 84, 9, 0,
        3, 94, 204, 195, 89, 98, 204, 195, 89, 117, 120, 11, 0, 1, 4, 140, 102, 0, 0,
        4, 140, 102, 0, 0, 80, 75, 3, 4, 10, 0, 0, 0, 0, 0, 130, 131, 53, 75, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 0, 28, 0, 116, 101, 115, 116, 47, 115, 117,
        98, 100, 105, 114, 47, 85, 84, 9, 0, 3, 116, 204, 195, 89, 134, 204, 195,
        89, 117, 120, 11, 0, 1, 4, 140, 102, 0, 0, 4, 140, 102, 0, 0, 80, 75, 3, 4,
        10, 0, 0, 0, 0, 0, 130, 131, 53, 75, 227, 250, 30, 37, 12, 0, 0, 0, 12, 0, 0,
        0, 21, 0, 28, 0, 116, 101, 115, 116, 47, 115, 117, 98, 100, 105, 114, 47, 116,
        101, 115, 116, 65, 46, 116, 120, 116, 85, 84, 9, 0, 3, 116, 204, 195, 89, 116,
        204, 195, 89, 117, 120, 11, 0, 1, 4, 140, 102, 0, 0, 4, 140, 102, 0, 0, 115,
        117, 98, 100, 105, 114, 116, 101, 115, 116, 65, 10, 80, 75, 3, 4, 10, 0, 0, 0,
        0, 0, 109, 131, 53, 75, 237, 78, 102, 83, 6, 0, 0, 0, 6, 0, 0, 0, 14, 0, 28,
        0, 116, 101, 115, 116, 47, 116, 101, 115, 116, 65, 46, 116, 120, 116, 85, 84,
        9, 0, 3, 78, 204, 195, 89, 78, 204, 195, 89, 117, 120, 11, 0, 1, 4, 140, 102,
        0, 0, 4, 140, 102, 0, 0, 116, 101, 115, 116, 65, 10, 80, 75, 1, 2, 30, 3, 10,
        0, 0, 0, 0, 0, 117, 131, 53, 75, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 24,
        0, 0, 0, 0, 0, 0, 0, 16, 0, 253, 65, 0, 0, 0, 0, 116, 101, 115, 116, 47, 85,
        84, 5, 0, 3, 94, 204, 195, 89, 117, 120, 11, 0, 1, 4, 140, 102, 0, 0, 4, 140,
        102, 0, 0, 80, 75, 1, 2, 30, 3, 10, 0, 0, 0, 0, 0, 130, 131, 53, 75, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 0, 24, 0, 0, 0, 0, 0, 0, 0, 16, 0, 253, 65, 63,
        0, 0, 0, 116, 101, 115, 116, 47, 115, 117, 98, 100, 105, 114, 47, 85, 84, 5,
        0, 3, 116, 204, 195, 89, 117, 120, 11, 0, 1, 4, 140, 102, 0, 0, 4, 140, 102,
        0, 0, 80, 75, 1, 2, 30, 3, 10, 0, 0, 0, 0, 0, 130, 131, 53, 75, 227, 250, 30,
        37, 12, 0, 0, 0, 12, 0, 0, 0, 21, 0, 24, 0, 0, 0, 0, 0, 1, 0, 0, 0, 180, 129,
        133, 0, 0, 0, 116, 101, 115, 116, 47, 115, 117, 98, 100, 105, 114, 47, 116,
        101, 115, 116, 65, 46, 116, 120, 116, 85, 84, 5, 0, 3, 116, 204, 195, 89, 117,
        120, 11, 0, 1, 4, 140, 102, 0, 0, 4, 140, 102, 0, 0, 80, 75, 1, 2, 30, 3, 10,
        0, 0, 0, 0, 0, 109, 131, 53, 75, 237, 78, 102, 83, 6, 0, 0, 0, 6, 0, 0, 0, 14,
        0, 24, 0, 0, 0, 0, 0, 1, 0, 0, 0, 180, 129, 224, 0, 0, 0, 116, 101, 115, 116,
        47, 116, 101, 115, 116, 65, 46, 116, 120, 116, 85, 84, 5, 0, 3, 78, 204, 195,
        89, 117, 120, 11, 0, 1, 4, 140, 102, 0, 0, 4, 140, 102, 0, 0, 80, 75, 5, 6, 0,
        0, 0, 0, 4, 0, 4, 0, 76, 1, 0, 0, 46, 1, 0, 0, 0, 0, 80, 75, 3, 4, 10, 0, 0, 0,
        0, 0, 230, 134, 53, 75, 102, 214, 67, 99, 2, 0, 0, 0, 2, 0, 0, 0, 17, 0, 28, 0,
        116, 101, 115, 116, 47, 115, 117, 98, 100, 105, 114, 47, 116, 101, 115, 116,
        65, 85, 84, 9, 0, 3, 207, 210, 195, 89, 207, 210, 195, 89, 117, 120, 11, 0, 1,
        4, 140, 102, 0, 0, 4, 140, 102, 0, 0, 66, 10, 80, 75, 3, 4, 10, 0, 0, 0, 0,
        0, 253, 134, 53, 75, 39, 231, 88, 122, 2, 0, 0, 0, 2, 0, 0, 0, 10, 0, 28, 0,
        116, 101, 115, 116, 47, 116, 101, 115, 116, 67, 85, 84, 9, 0, 3, 253, 210,
        195, 89, 253, 210, 195, 89, 117, 120, 11, 0, 1, 4, 140, 102, 0, 0, 4, 140,
        102, 0, 0, 67, 10, 80, 75, 3, 4, 10, 0, 0, 0, 0, 0, 211, 134, 53, 75, 165,
        133, 110, 72, 2, 0, 0, 0, 2, 0, 0, 0, 10, 0, 28, 0, 116, 101, 115, 116, 47,
        116, 101, 115, 116, 65, 85, 84, 9, 0, 3, 173, 210, 195, 89, 173, 210, 195, 89,
        117, 120, 11, 0, 1, 4, 140, 102, 0, 0, 4, 140, 102, 0, 0, 65, 10, 80, 75, 1,
        2, 30, 3, 10, 0, 0, 0, 0, 0, 253, 134, 53, 75, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 5, 0, 24, 0, 0, 0, 0, 0, 0, 0, 16, 0, 253, 65, 0, 0, 0, 0, 116, 101, 115,
        116, 47, 85, 84, 5, 0, 3, 253, 210, 195, 89, 117, 120, 11, 0, 1, 4, 140, 102,
        0, 0, 4, 140, 102, 0, 0, 80, 75, 1, 2, 30, 3, 10, 0, 0, 0, 0, 0, 230, 134, 53,
        75, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 0, 24, 0, 0, 0, 0, 0, 0, 0, 16,
        0, 253, 65, 63, 0, 0, 0, 116, 101, 115, 116, 47, 115, 117, 98, 100, 105, 114,
        47, 85, 84, 5, 0, 3, 207, 210, 195, 89, 117, 120, 11, 0, 1, 4, 140, 102, 0,
        0, 4, 140, 102, 0, 0, 80, 75, 1, 2, 30, 3, 10, 0, 0, 0, 0, 0, 130, 131, 53,
        75, 227, 250, 30, 37, 12, 0, 0, 0, 12, 0, 0, 0, 21, 0, 24, 0, 0, 0, 0, 0, 1,
        0, 0, 0, 180, 129, 133, 0, 0, 0, 116, 101, 115, 116, 47, 115, 117, 98, 100,
        105, 114, 47, 116, 101, 115, 116, 65, 46, 116, 120, 116, 85, 84, 5, 0, 3, 116,
        204, 195, 89, 117, 120, 11, 0, 1, 4, 140, 102, 0, 0, 4, 140, 102, 0, 0, 80,
        75, 1, 2, 30, 3, 10, 0, 0, 0, 0, 0, 109, 131, 53, 75, 237, 78, 102, 83, 6, 0,
        0, 0, 6, 0, 0, 0, 14, 0, 24, 0, 0, 0, 0, 0, 1, 0, 0, 0, 180, 129, 224, 0, 0,
        0, 116, 101, 115, 116, 47, 116, 101, 115, 116, 65, 46, 116, 120, 116, 85, 84,
        5, 0, 3, 78, 204, 195, 89, 117, 120, 11, 0, 1, 4, 140, 102, 0, 0, 4, 140, 102,
        0, 0, 80, 75, 1, 2, 30, 3, 10, 0, 0, 0, 0, 0, 144, 131, 53, 75, 204, 176, 61,
        249, 144, 2, 0, 0, 144, 2, 0, 0, 13, 0, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 180,
        129, 46, 1, 0, 0, 116, 101, 115, 116, 47, 116, 101, 115, 116, 46, 122, 105,
        112, 85, 84, 5, 0, 3, 143, 204, 195, 89, 117, 120, 11, 0, 1, 4, 140, 102, 0,
        0, 4, 140, 102, 0, 0, 80, 75, 1, 2, 30, 3, 10, 0, 0, 0, 0, 0, 230, 134, 53, 75,
        102, 214, 67, 99, 2, 0, 0, 0, 2, 0, 0, 0, 17, 0, 24, 0, 0, 0, 0, 0, 1, 0, 0,
        0, 180, 129, 5, 4, 0, 0, 116, 101, 115, 116, 47, 115, 117, 98, 100, 105, 114,
        47, 116, 101, 115, 116, 65, 85, 84, 5, 0, 3, 207, 210, 195, 89, 117, 120, 11,
        0, 1, 4, 140, 102, 0, 0, 4, 140, 102, 0, 0, 80, 75, 1, 2, 30, 3, 10, 0, 0, 0,
        0, 0, 253, 134, 53, 75, 39, 231, 88, 122, 2, 0, 0, 0, 2, 0, 0, 0, 10, 0, 24,
        0, 0, 0, 0, 0, 1, 0, 0, 0, 180, 129, 82, 4, 0, 0, 116, 101, 115, 116, 47, 116,
        101, 115, 116, 67, 85, 84, 5, 0, 3, 253, 210, 195, 89, 117, 120, 11, 0, 1, 4,
        140, 102, 0, 0, 4, 140, 102, 0, 0, 80, 75, 1, 2, 30, 3, 10, 0, 0, 0, 0, 0,
        211, 134, 53, 75, 165, 133, 110, 72, 2, 0, 0, 0, 2, 0, 0, 0, 10, 0, 24, 0, 0,
        0, 0, 0, 1, 0, 0, 0, 180, 129, 152, 4, 0, 0, 116, 101, 115, 116, 47, 116, 101,
        115, 116, 65, 85, 84, 5, 0, 3, 173, 210, 195, 89, 117, 120, 11, 0, 1, 4, 140,
        102, 0, 0, 4, 140, 102, 0, 0, 80, 75, 5, 6, 0, 0, 0, 0, 8, 0, 8, 0, 150, 2,
        0, 0, 222, 4, 0, 0, 0, 0, 80, 75, 3, 4, 10, 0, 0, 0, 0, 0, 211, 134, 53, 75,
        165, 133, 110, 72, 2, 0, 0, 0, 2, 0, 0, 0, 10, 0, 28, 0, 116, 101, 115, 116,
        47, 116, 101, 115, 116, 65, 85, 84, 9, 0, 3, 173, 210, 195, 89, 3, 211, 195,
        89, 117, 120, 11, 0, 1, 4, 140, 102, 0, 0, 4, 140, 102, 0, 0, 65, 10, 80, 75,
        1, 2, 30, 3, 10, 0, 0, 0, 0, 0, 8, 135, 53, 75, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 5, 0, 24, 0, 0, 0, 0, 0, 0, 0, 16, 0, 253, 65, 0, 0, 0, 0, 116, 101,
        115, 116, 47, 85, 84, 5, 0, 3, 16, 211, 195, 89, 117, 120, 11, 0, 1, 4, 140,
        102, 0, 0, 4, 140, 102, 0, 0, 80, 75, 1, 2, 30, 3, 10, 0, 0, 0, 0, 0, 230,
        134, 53, 75, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 0, 24, 0, 0, 0, 0, 0, 0,
        0, 16, 0, 253, 65, 63, 0, 0, 0, 116, 101, 115, 116, 47, 115, 117, 98, 100,
        105, 114, 47, 85, 84, 5, 0, 3, 207, 210, 195, 89, 117, 120, 11, 0, 1, 4, 140,
        102, 0, 0, 4, 140, 102, 0, 0, 80, 75, 1, 2, 30, 3, 10, 0, 0, 0, 0, 0, 230,
        134, 53, 75, 102, 214, 67, 99, 2, 0, 0, 0, 2, 0, 0, 0, 17, 0, 24, 0, 0, 0, 0,
        0, 1, 0, 0, 0, 180, 129, 133, 0, 0, 0, 116, 101, 115, 116, 47, 115, 117, 98,
        100, 105, 114, 47, 116, 101, 115, 116, 65, 85, 84, 5, 0, 3, 207, 210, 195,
        89, 117, 120, 11, 0, 1, 4, 140, 102, 0, 0, 4, 140, 102, 0, 0, 80, 75, 1, 2,
        30, 3, 10, 0, 0, 0, 0, 0, 2, 135, 53, 75, 162, 170, 2, 92, 138, 7, 0, 0, 138,
        7, 0, 0, 13, 0, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 180, 129, 210, 0, 0, 0, 116,
        101, 115, 116, 47, 116, 101, 115, 116, 46, 122, 105, 112, 85, 84, 5, 0, 3,
        3, 211, 195, 89, 117, 120, 11, 0, 1, 4, 140, 102, 0, 0, 4, 140, 102, 0, 0,
        80, 75, 1, 2, 30, 3, 10, 0, 0, 0, 0, 0, 211, 134, 53, 75, 165, 133, 110, 72,
        2, 0, 0, 0, 2, 0, 0, 0, 10, 0, 24, 0, 0, 0, 0, 0, 1, 0, 0, 0, 180, 129, 163,
        8, 0, 0, 116, 101, 115, 116, 47, 116, 101, 115, 116, 65, 85, 84, 5, 0, 3,
        173, 210, 195, 89, 117, 120, 11, 0, 1, 4, 140, 102, 0, 0, 4, 140, 102, 0, 0,
        80, 75, 5, 6, 0, 0, 0, 0, 5, 0, 5, 0, 151, 1, 0, 0, 233, 8, 0, 0, 0, 0]


    if sys.version_info[0] < 3:
        zipContents = ''.join([chr(x) for x in zipArchive])
    else:
        zipContents = bytes(zipArchive)

    def testGetDataFromFile(self):

        try:
            fd, filename = tempfile.mkstemp()
            os.write(fd, self.zipContents)
            os.close(fd)

            zipReader = ZipReader(filename)

            mibinfo, data = zipReader.getData('testA')

            assert data == 'A\n'

        finally:
            try:
                os.remove(filename)

            except:
                pass

    def testGetInnerZipData(self):

        try:
            fd, filename = tempfile.mkstemp()
            os.write(fd, self.zipContents)
            os.close(fd)

            zipReader = ZipReader(filename)

            mibinfo, data = zipReader.getData('testC')

            assert data == 'C\n'

        finally:
            try:
                os.remove(filename)

            except:
                pass


suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite)