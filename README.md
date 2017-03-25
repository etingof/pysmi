
SNMP MIB parser
---------------
[![Python Versions](https://img.shields.io/pypi/pyversions/pysmi.svg)](https://pypi.python.org/pypi/pysmi/)
[![Build status](https://travis-ci.org/etingof/pysmi.svg?branch=master)](https://secure.travis-ci.org/etingof/pysmi)
[![Coverage Status](https://img.shields.io/codecov/c/github/etingof/pysmi.svg)](https://codecov.io/github/etingof/pysmi)
[![GitHub license](https://img.shields.io/badge/license-BSD-blue.svg)](https://raw.githubusercontent.com/etingof/pysmi/master/LICENSE.rst)

PySMI is a pure-Python implementation of SNMP SMI MIB parser. This tool
is designed to turn ASN.1 MIBs into various formats. As of this moment, JSON and
[pysnmp](https://github.com/etingof/pysnmp) modules can be generated from ASN.1 MIBs.

Features
--------

* Understands SMIv1, SMIv2 and de-facto dialects
* Turns MIBs into pysnmp classes and JSON documents
* Maintain an index of MIB objects
* Automatically downloads ASN.1 MIBs from various sources
* 100% Python, works with Python 2.4 up to Python 3.6

Rendered pysmi documentation can be found at [pysmi site](http://pysmi.sf.net).

How to use PySMI
----------------

If you are using pysnmp, you might never notice pysmi presence - pysnmp will call it for MIB
download and compilation automatically.

If you want to compile ASN.1 MIB into PySNMP module by hand, use *mibdump.py* tool
like this:

```
$ mibdump.py CISCO-MIB
Source MIB repositories: file:///usr/share/snmp/mibs, http://mibs.snmplabs.com/asn1/@mib@
Borrow missing/failed MIBs from: http://mibs.snmplabs.com/pysnmp/notexts/@mib@
Existing/compiled MIB locations: pysnmp.smi.mibs, pysnmp_mibs
Compiled MIBs destination directory: /Users/ilya/.pysnmp/mibs
MIBs excluded from code generation: RFC-1212, RFC-1215, RFC1065-SMI, RFC1155-SMI,
RFC1158-MIB, RFC1213-MIB, SNMP-FRAMEWORK-MIB, SNMP-TARGET-MIB, SNMPv2-CONF, SNMPv2-SMI,
SNMPv2-TC, SNMPv2-TM, TRANSPORT-ADDRESS-MIB
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
Up to date MIBs: IANAifType-MIB, INET-ADDRESS-MIB, RFC-1212, RFC1155-SMI,
RFC1213-MIB, SNMPv2-CONF, SNMPv2-MIB, SNMPv2-SMI, SNMPv2-TC
Missing source MIBs: 
Ignored MIBs: 
Failed MIBs: 
```

You can also turn ASN.1 MIB into a general purpose JSON document:

```
$ mibdump.py --generate-mib-texts  --destination-format json IF-MIB
Source MIB repositories: file:///usr/share/snmp/mibs, http://mibs.snmplabs.com/asn1/@mib@
Borrow missing/failed MIBs from: http://mibs.snmplabs.com/json/fulltexts/@mib@
Existing/compiled MIB locations: 
Compiled MIBs destination directory: .
MIBs excluded from code generation: RFC-1212, RFC-1215, RFC1065-SMI, RFC1155-SMI,
RFC1158-MIB, RFC1213-MIB, SNMPv2-CONF, SNMPv2-SMI, SNMPv2-TC, SNMPv2-TM
MIBs to compile: IF-MIB
Destination format: json
Parser grammar cache directory: not used
Also compile all relevant MIBs: yes
Rebuild MIBs regardless of age: yes
Do not create/update MIBs: no
Byte-compile Python modules: no (optimization level no)
Ignore compilation errors: no
Generate OID->MIB index: no
Generate texts in MIBs: yes
Try various filenames while searching for MIB module: yes
Created/updated MIBs: IANAifType-MIB, IF-MIB, SNMPv2-MIB
Pre-compiled MIBs borrowed: 
Up to date MIBs: SNMPv2-CONF, SNMPv2-SMI, SNMPv2-TC
Missing source MIBs: 
Ignored MIBs: 
Failed MIBs: 
```

JSON document containing
[IF-MIB module](http://mibs.snmplabs.com/asn1/IF-MIB>)
would hold information such as:

```
   {
      "ifMIB": {
          "name": "ifMIB",
          "oid": "1.3.6.1.2.1.31",
          "class": "moduleidentity",
          "revisions": [
            "2007-02-15 00:00",
            "1996-02-28 21:55",
            "1993-11-08 21:55"
          ]
        },

      ...
      "ifTestTable": {
        "name": "ifTestTable",
        "oid": "1.3.6.1.2.1.31.1.3",
        "class": "objecttype",
        "maxaccess": "not-accessible"
      },
      "ifTestEntry": {
        "name": "ifTestEntry",
        "oid": "1.3.6.1.2.1.31.1.3.1",
        "class": "objecttype",
        "maxaccess": "not-accessible",
        "augmention": {
          "name": "ifTestEntry",
          "module": "IF-MIB",
          "object": "ifEntry"
        }
      },
      "ifTestId": {
        "name": "ifTestId",
        "oid": "1.3.6.1.2.1.31.1.3.1.1",
        "class": "objecttype",
        "syntax": {
          "type": "TestAndIncr",
          "class": "type"
        },
        "maxaccess": "read-write"
      },
      ...
   }
```

In general, converted MIBs capture all aspects of original (ASN.1) MIB contents
and layout. The snippet above is just an example, here is the complete
[IF-MIB.json](http://mibs.snmplabs.com/json/fulltext/IF-MIB.json)
file.

Besides 1-to-1 MIB conversion, PySMI library can produce JSON index to facilitate
fast MIB information lookup across large collection of MIB files. For example,
JSON index for
[IP-MIB.json](http://mibs.snmplabs.com/json/asn1/IP-MIB),
[TCP-MIB.json](http://mibs.snmplabs.com/json/asn1/TCP-MIB) and
[UDP-MIB.json](http://mibs.snmplabs.com/json/asn1/UDP-MIB)
modules would keep information like this:

```
   {
      "compliance": {
         "1.3.6.1.2.1.48.2.1.1": [
           "IP-MIB"
         ],
         "1.3.6.1.2.1.49.2.1.1": [
           "TCP-MIB"
         ],
         "1.3.6.1.2.1.50.2.1.1": [
           "UDP-MIB"
         ]
      },
      "identity": {
          "1.3.6.1.2.1.48": [
            "IP-MIB"
          ],
          "1.3.6.1.2.1.49": [
            "TCP-MIB"
          ],
          "1.3.6.1.2.1.50": [
            "UDP-MIB"
          ]
      },
      "oids": {
          "1.3.6.1.2.1.4": [
            "IP-MIB"
          ],
          "1.3.6.1.2.1.5": [
            "IP-MIB"
          ],
          "1.3.6.1.2.1.6": [
            "TCP-MIB"
          ],
          "1.3.6.1.2.1.7": [
            "UDP-MIB"
          ],
          "1.3.6.1.2.1.49": [
            "TCP-MIB"
          ],
          "1.3.6.1.2.1.50": [
            "UDP-MIB"
          ]
      }
   }
```

With this example, *compliance* and *identity* keys point to
*MODULE-COMPLIANCE* and *MODULE-IDENTITY* MIB objects, *oids*
list top-level OIDs branches defined in MIB modules. Full index
build over thousands of MIBs could be seen
[here](http://mibs.snmplabs.com/json/index.json).

The PySMI library can automatically fetch required MIBs from HTTP, FTP sites
or local directories. You could configure any MIB source available to you (including
[http://mibs.snmplabs.com/asn1/](http://mibs.snmplabs.com/asn1/)) for that purpose.

How to get PySMI
----------------

The pysmi package is distributed under terms and conditions of 2-clause
BSD [license](http://pyasn1.sourceforge.net/license.html). Source code is freely
available as a GitHub [repo](https://github.com/etingof/pysmi).

You could `pip install pysmi` or download it from [PyPI](https://pypi.python.org/pypi/pysmi).

If something does not work as expected,
[open an issue](https://github.com/etingof/pysmi/issues) at GitHub or
post your question [on Stack Overflow](http://stackoverflow.com/questions/ask).

Copyright (c) 2015-2017, [Ilya Etingof](mailto://etingof@gmail.com).
All rights reserved.
