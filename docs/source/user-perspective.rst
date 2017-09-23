
PySMI: user perspective
=======================

.. toctree::
   :maxdepth: 2

The *mibdump.py* tool is a command-line frontend to the PySMI library. This
tool can be used for automatic downloading and transforming SNMP MIB modules
into various formats.

.. code-block:: bash

   $ mibdump.py -h
   Synopsis:
     SNMP SMI/MIB files conversion tool
   Documentation:
     http://pysmi.sourceforge.net
   Usage: mibdump.py [--help]
         [--version]
         [--quiet]
         [--debug=<all|borrower|codegen|compiler|grammar|lexer|parser|reader|searcher|writer>]
         [--mib-source=<URI>]
         [--mib-searcher=<PATH|PACKAGE>]
         [--mib-stub=<MIB-NAME>]
         [--mib-borrower=<PATH>]
         [--destination-format=<FORMAT>]
         [--destination-directory=<DIRECTORY>]
         [--cache-directory=<DIRECTORY>]
         [--disable-fuzzy-source]
         [--no-dependencies]
         [--no-python-compile]
         [--python-optimization-level]
         [--ignore-errors]
         [--build-index]
         [--rebuild]
         [--dry-run]
         [--no-mib-writes]
         [--generate-mib-texts]
         [--keep-texts-layout]
         <MIB|URI> [<MIB|URI> [...]]]
   Where:
       URI         - file, zip, http, https, ftp, sftp schemes are supported.
                     Use @mib@ placeholder token in URI to refer directly to
                     the required MIB module when source does not support
                     directory listing (e.g. HTTP).
       FORMAT      - pysnmp, json, null
       MIB or URI  - Either MIB module name or a URI pointing to a MIB source.
                     In the latter case all MIBs will be pulled and compiled.


When JSON destination format is requested, for each MIB module *mibdump.py*
will produce a JSON document containing all MIB objects. For example,
`IF-MIB <http://mibs.snmplabs.com/asn1/IF-MIB>`_ module in JSON form
would look like:

.. code-block:: json

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

In general, JSON MIB captures all aspects of original (ASN.1) MIB contents
and layout. The snippet above is just an example, here is the complete
`IF-MIB.json <http://mibs.snmplabs.com/json/fulltext/IF-MIB.json>`_
file.

Specifying MIB source
---------------------

The --mib-source option can be given multiple times. Each instance of
--mib-source must specify a URL where ASN.1 MIB modules should be
looked up and downloaded from. At this moment three MIB sourcing
methods are supported:

* Local files. This could be a top-level directory where MIB files are
  located. Subdirectories will be automatically traversed as well. 
  Example: file:///usr/share/snmp
* ZIP archives containing MIB files. Subdirectories and embedded ZIP
  archives will be automatically traversed.
  Example: zip://mymibs.zip
* HTTP/HTTPS. A fully specified URL where MIB module name is specified by
  a @mib@ placeholder. When specific MIB is looked up, PySMI will replace
  that placeholder with MIB module name it is looking for. 
  Example: `http://mibs.snmplabs.com/asn1/@mib@ <http://mibs.snmplabs.com/asn1/>`_
* SFTP/FTP. A fully specified URL including FTP username and password. 
  MIB module name is specified by a @mib@ placeholder. When specific MIB
  is looked up, PySMI will replace that placeholder with MIB module name
  it is looking for. 
  Example: `http://mibs.snmplabs.com/asn1/@mib@ <http://mibs.snmplabs.com/asn1/>`_

When trying to fetch a MIB module, the *mibdump.py* tool will try each of
configured --mib-source transports in order of specification till 
first successful hit.

By default *mibdump.py* will search:

* file:///usr/share/snmp
* http://mibs.snmplabs.com/asn1/@mib@

Once another --mib-source option is given, those defaults will not be used
and should be manually given to *mibdump.py* if needed.

Fuzzing MIB module names
------------------------

There is no single convention on how MIB module files should be named. By
default *mibdump.py* will try a handful of guesses when trying to find a file
containing specific MIB module. It will try upper and lower cases, a file 
named after MIB module, try adding different extensions to a file (.mib,
.my etc), try adding/cutting the '-MIB' part of the file name.
If nothing matches, *mibdump.py* will consider that probed --mib-source
does not contain MIB module it is looking for.

There is a small chance, though, that fuzzy matching may result in getting
a wrong MIB. If that happens, you can disable the above fuzziness by
giving *mibdump.py* the --disable-fuzzy-source flag.

Mass processing MIB files
-------------------------

Besides applying transformation on specific MIB modules, you can
point pysmi to a MIB source in form of a URI. The library will then
read all MIB modules from that source one by one and converting each
into target format. That way may be especially handy when your MIB
files names differ from canonical MIB modules names.

Avoiding excessive transformation
---------------------------------

It well may happen that many MIB modules refer to a common single MIB
module. In that case *mibdump.py* may transform it many times unless you
tell *mibdump.py* where to search for already transformed MIBs. That place
could of course be a directory where *mibdump.py* writes its transforms into
and/or some other local locations.

The --mib-searcher option specifies either local directory or importable
Python package (applicable to pysnmp transformation) containing transformed
MIB modules. Multiple --mib-searcher options could be given, *mibdump.py*
will use each of them in order of specification till first hit.

If no transformed MIB module is found, *mibdump.py* will go on running its full
transformation cycle.

By default *mibdump.py* will use:

* --mib-searcher=$HOME/.pysnmp/mibs
* --mib-searcher=pysnmp_mibs

Once another --mib-searcher option is given, those defaults will not be used
and should be manually given to *mibdump.py* if needed.

Blacklisting MIBs
-----------------

Some MIBs may not be automatically transformed into another form and 
therefore must be explicitly excluded from processing. Such MIBs are
normally manually implemented for each target MIB format. Examples
include MIBs containing base SMI types or ASN.1 MACRO definitions
(SNMPv2-SMI, SNMPV2-TC), initially compiled but later manually modified 
MIBs and others.

Default list of blacklisted MIBs for pysnmp transformation target 
is: RFC-1212, RFC-1215, RFC1065-SMI, RFC1155-SMI, RFC1158-MIB, 
RFC1213-MIB, SNMP-FRAMEWORK-MIB, SNMP-TARGET-MIB, SNMPv2-CONF, SNMPv2-SMI,
SNMPv2-TC, SNMPv2-TM, TRANSPORT-ADDRESS-MIB.

If you need to modify this list use the --mib-stub option.

Dealing with broken MIBs
------------------------

Curiously enough, some MIBs coming from quite prominent vendors 
appear syntactically incorrect. That leads to MIB compilers fail on
such MIBs. While many MIB compiler implementations (PySMI included)
introduce workarounds and grammar relaxations allowing slightly
broken MIBs to compile, however severely broken MIBs can't be
reliably compiled. 

As another workaround PySMI offers the *borrow* feature. It allows
PySMI to fetch already transformed MIBs even if corresponding
ASN.1 MIB can't be found or parsed.

Default source of pre-compiled MIBs for pysnmp target is:

* http://mibs.snmplabs.com/pysnmp/fulltexts/@mib@
* http://mibs.snmplabs.com/pysnmp/notexts/@mib@

If you wish to modify this default list use one or more
--mib-borrower options.

Choosing target transformation
------------------------------

PySMI design allows many transformation formats to be
supported in form of specialized code generation components.
At the moment PySMI can produce MIBs in form of pysnmp classes
and JSON documents.

JSON document schema is chosen to preserve as much of MIB
information as possible. There's no established JSON schema
known to the authors.

Setting destination directory
-----------------------------

By default *mibdump.py* writes pysnmp MIBs into:

* $HOME/.pysnmp/mibs  (on UNIX)
* @HOME@\PySNMP Configuration\MIBs\  (on Windows)

and JSON files in current working directory.

Use --destination-directory option to change default output
diretory.

Performing unconditional transformation
---------------------------------------

By default PySMI will avoid creating new transformations if fresh
enough versions already exist. By using --rebuild option you could
trick PySMI doing requested transformation for all given MIB modules.

Ignoring transformation errors
------------------------------

By default PySMI will stop on first fatal error occurred during
transformations of a series of MIBs. If you wish PySMI to ignore
fatal errors and therefore skipping failed MIB, use the --ignore-errors
option.

Keep in mind that skipping transformation of MIBs that are imported
by other MIBs might make dependant MIBs inconsistent for use.

Skipping dependencies
---------------------

Most MIBs rely on other MIBs for their operations. This is indicated
by the IMPORT statement in ASN.1 language. PySMI attempts to transform
all MIBs IMPORT'ed by MIB being transformed. That is done in recurrsive
manner.

By using --no-dependencies flag you can tell PySMI not to transform any
MIBs other than those explicitly requested to be transformed.

Keep in mind that skipping dependencies may make the whole set of
transformed MIBs inconsistent.

Generating MIB texts
--------------------

Most MIBs are very verbose. They contain many human-oriented descriptions
and clarifications written in plain English. Those texts may be useful 
for MIB browser applications (to display those texts to human operator)
but might not make any sense in other applications.

To save space and CPU time, PySMI does not by default include those texts 
into transformed MIBs. However this can be reverted by adding
--generate-mib-texts option.

When MIB texts are generated, whitespaces and new lines are stripped by
default. Sometimes that breaks down ASCII art should it occur in MIB texts.
To preserve original text formatting, --keep-texts-layout option may
be used.

Building MIB indices
--------------------

If --build-index option is given, depending on the destination format chosen,
the *mibdump.py* tool may create new (or update existing) document containing
MIB information in a form that is convenient for querying cornerstone
properties of MIB files.

For example, building JSON index for
`IP-MIB.json <http://mibs.snmplabs.com/json/asn1/IP-MIB>`_,
`TCP-MIB.json <http://mibs.snmplabs.com/json/asn1/TCP-MIB>`_ and
`UDP-MIB.json <http://mibs.snmplabs.com/json/asn1/UDP-MIB>`_
MIB modules would emit something like this:

.. code-block:: json

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

With this example, *compliance* and *identity* keys point to
*MODULE-COMPLIANCE* and *MODULE-IDENTITY* MIB objects, *oids*
list top-level OIDs branches defined in MIB modules. Full index
build over thousands of MIBs could be seen
`here <http://mibs.snmplabs.com/json/index.json>`_.

Minor speedups
--------------

There are a few options that may improve PySMI performance.

The --cache-directory option may be used to point to a temporary
writable directory where PySMI parser (e.g. Ply) would store its 
lookup tables.

By default PySMI performing transformation into pysnmp format will 
also pre-compile Python source into interpreter bytecode. That takes
some time and space. If you wish not to cache Python bytecode
or to do that later, use the --no-python-compile option.

