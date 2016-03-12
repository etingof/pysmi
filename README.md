
SNMP MIB parser
---------------
[![Downloads](https://img.shields.io/pypi/dm/pysmi.svg)](https://pypi.python.org/pypi/pysmi)
[![Build status](https://travis-ci.org/etingof/pysmi.svg?branch=master)](https://secure.travis-ci.org/etingof/pysmi)
[![Coverage Status](https://img.shields.io/codecov/c/github/etingof/pysmi.svg)](https://codecov.io/github/etingof/pysmi)
[![GitHub license](https://img.shields.io/badge/license-BSD-blue.svg)](https://raw.githubusercontent.com/etingof/pysmi/master/LICENSE.txt)

This is a pure-Python implementation of SNMP SMI MIB parser. This software
is designed to accommodate multiple code generation backends in hope
that they could be useful for SNMP MIB format conversions.

As of this moment, the only code generation backend currently implemented
is for [pysnmp](http://pysnmp.sf.net) MIB modules generation.

Download
--------

The pysmi package is distributed under terms and conditions of 2-clause
BSD [license](http://pysmi.sourceforge.net/license.html). Source code is freely
available as a Github [repo](https://github.com/etingof/pysmi).

Installation
------------

Download pysmi from [PyPI](https://pypi.python.org/pypi/pysmi) or just run:

```bash
$ pip install pysmi
```

How to use pysmi
----------------

If you are using pysnmp, you might never notice pysmi presense - pysnmp will call it for MIB
download and compilation automatically.

If you want to compile ASN.1 MIB into PySNMP module by hand, use *mibdump.py* tool
like this:

```
$ mibdump.py CISCO-MIB
Source MIB repositories: file:///usr/share/snmp/mibs, http://mibs.snmplabs.com/asn1/@mib@
Borrow missing/failed MIBs from: http://mibs.snmplabs.com/pysnmp/notexts/@mib@
Existing/compiled MIB locations: pysnmp.smi.mibs, pysnmp_mibs
Compiled MIBs destination directory: /Users/ilya/.pysnmp/mibs
MIBs excluded from code generation: RFC-1212, RFC-1215, RFC1065-SMI, RFC1155-SMI, RFC1158-MIB, RFC1213-MIB, SNMP-FRAMEWORK-MIB, SNMP-TARGET-MIB, SNMPv2-CONF, SNMPv2-SMI, SNMPv2-TC, SNMPv2-TM, TRANSPORT-ADDRESS-MIB
MIBs to compile: CISCO-MIB
Destination format: pysnmp
Parser grammar cache directory: not used
Also compile all relevant MIBs: yes
Rebuild MIBs regardless of age: no
Do not create/update MIBs: no
Byte-compile Python modules: yes (optimization level 0)
Ignore compilation errors: no
Generate OID->MIB index: no
Generate texts in MIBs: no
Try various filenames while searching for MIB module: yes
Created/updated MIBs: CISCO-MIB IF-MIB IP-MIB TCP-MIB
Pre-compiled MIBs borrowed: 
Up to date MIBs: IANAifType-MIB, INET-ADDRESS-MIB, RFC-1212, RFC1155-SMI, RFC1213-MIB, SNMPv2-CONF, SNMPv2-MIB, SNMPv2-SMI, SNMPv2-TC
Missing source MIBs: 
Ignored MIBs: 
Failed MIBs: 
```

The pysmi library can automatically fetch required MIBs from HTTP, FTP sites
or local directories. You could configure any MIB source available to you (including
[http://mibs.snmplabs.com/asn1/](http://mibs.snmplabs.com/asn1/)) for that purpose.

Documentation
-------------

Detailed information on pysmi library interfaces be found at [pysmi site](http://pysmi.sf.net).

Feedback
--------

I'm interested in bug reports and fixes, suggestions and improvements. Your pull requests
are very welcome as well!

Copyright (c) 2005-2016, [Ilya Etingof](http://ilya@glas.net). All rights reserved.
