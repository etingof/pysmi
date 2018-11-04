
The *mibcopy* tool
==================

.. toctree::
   :maxdepth: 2

The *mibcopy.py* tool attempts to normalize the file name of the MIB file.

It turned out that sometimes vendors name their MIBs in any possible way,
not necessarily after the canonical MIB name. This causes problems to the
MIB consumers as they may not be able to locate the MIB they need on the
file system.

The way how *mibcopy.py* works is that it tries to read the MIB from
the given file (or all files from a given directory or archive), parse
MIB's canonical name from the contents of the file. Based on that, the
tool tries to rename MIB file into the name which is the same as canonical
MIB name. If *mibcopy.py* encounters the same named file already present
on the file system, it reads it up to see its revision date. Then the
tool compares the revision dates of the colliding MIB files and either
overrides the offending file or drops the file being copied as outdated.

The ultimate goal is to end up with the latest versions of the MIB files
all named after their canonical names.

.. code-block:: bash

    $ mibcopy.py --help
    Synopsis:
      SNMP SMI/MIB files copying tool. When given MIB file(s) or
      directory(ies) on input and a destination directory, the tool
      parses MIBs to figure out their canonical MIB module name and
      the latest revision date, then copies MIB module on input
      into the destination directory under its MIB module name
      *if* there is no such file already or its revision date is
      older.

    Documentation:
      http://snmplabs.com/pysmi
    Usage: mibcopy.py [--help]
          [--version]
          [--verbose]
          [--quiet]
          [--debug=<all|borrower|codegen|compiler|grammar|lexer|
                    parser|reader|searcher|writer>]
          [--mib-source=<URI>]
          [--cache-directory=<DIRECTORY>]
          [--ignore-errors]
          [--dry-run]
          <SOURCE [SOURCE...]> <DESTINATION>
    Where:
        URI      - file, zip, http, https, ftp, sftp schemes are
                   supported. Use @mib@ placeholder token in URI to
                   refer directly to the required MIB module when
                   source does not support directory listing
                   (e.g. HTTP).

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

When trying to fetch a MIB module, the *mibcopy.py* tool will try each of
configured --mib-source transports in order of specification till 
first successful hit.

By default *mibcopy.py* will search:

* file:///usr/share/snmp
* http://mibs.snmplabs.com/asn1/@mib@

Once another --mib-source option is given, those defaults will not be used
and should be manually given to *mibcopy.py* if needed.

Setting destination directory
-----------------------------

The *mibcopy.py* writes MIBs into the *<DESTINATION>* directory.

Ignoring transformation errors
------------------------------

By default PySMI will stop on first fatal error occurred during
transformations of a series of MIBs. If you wish PySMI to ignore
fatal errors and therefore skipping failed MIB, use the --ignore-errors
option.

Keep in mind that skipping transformation of MIBs that are imported
by other MIBs might make dependant MIBs inconsistent for use.

Minor speedups
--------------

The --cache-directory option may be used to point to a temporary
writable directory where PySMI parser (e.g. Ply) would store its 
lookup tables. That should improve PySMI performance a tad bit.
