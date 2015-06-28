.. toctree::
   :maxdepth: 2

PySMI documentation
===================

The PySMI library and tools are designed to parse, verify and transform
SNMP SMI MIB modules. The ultimate goal of PySMI effort is to handle as 
much SMI syntax flavors and conversion operations as libsmi does but in
pure Python. PySMI's APIs are designed in modular, reusable and 
object-oriented fashion in hope to make PySMI useful for native Python
applications.

Top-level design
----------------

PySMI library is highly modular. The top-level component is called
*compiler* and it acts as main user-facing object. Most of other
components are plugged into the *compiler* object prior to its use.

Normally, user asks *compiler* to perform certain transformation of
named MIB module. Compiler will:

* Search its data sources for given MIB module (identified by name)
  noting their last modification times.
* Search compiler-managed repositories of already converted MIB modules
  for modules that are more recent than corresponding source MIB module.
* If freshly transformed MIB module is found, processing stops here.
* Otherwise compiler passes ASN.1 MIB module content to the *lexer*
  component.
* Lexer returns a sequence of tokenized ASN.1 MIB contents. Compiler
  then passes that sequence of tokens to the *parser* component.
* Parser runs LR algorithm on tokenized MIB thus transforming MIB
  contents into Abstract Syntax Tree (AST) and also noting what other
  MIB modules are referred to from the MIB being parsed.
* In case of parser failure, what is usually an indication of broken
  ASN.1 MIB syntax, compiler may attempt to fetch pre-transformed MIB
  contents from configured source. This process is called *borrowing*
  in PySMI.
* In case of successful parser completion, compiler will pass produced 
  AST to *code generator* component.
* Code generator walks its input AST and performs actual data 
  transformation.
* The above steps may be repeated for each of the MIB modules referred
  to as parser figures out. Once no more unresolved dependencies remain,
  compiler will call its *writer* component to store all transformed MIB
  modules.

The locaiton of ASN.1 MIB modules and flavor of their syntax, as well as
desired transformation format, is determined by respective components
chosen and configured to compiler.

User perspective
----------------

Although a collection of command-line tools for MIB management is
anticipated to appear on top of PySMI library, a single *mibdump*
tool is currently shipped with PySMI.

The mibdump tool can be used for automatic downoading and transformation
of specific MIB module 

|    $ mibdump.py --help
|    Usage: scripts/mibdump.py [--help]
|          [--version]
|          [--quiet]
|          [--debug=<all|borrower|codegen|compiler|grammar|lexer|
|                    parser|reader|searcher|writer>]
|          [--mib-source=<url>]
|          [--disable-fuzzy-source]
|          [--mib-searcher=<path|package>]
|          [--mib-stub=<mibname>]
|          [--mib-borrower=<path>]
|          [--destination-format=<format>]
|          [--destination-directory=<directory>]
|          [--cache-directory=<directory>]
|          [--no-dependencies]
|          [--no-python-compile]
|          [--python-optimization-level]
|          [--ignore-errors]
|          [--build-index]
|          [--rebuild]
|          [--dry-run]
|          [--generate-mib-texts]
|          [ mibfile [ mibfile [...]]]
|    Where:
|        url      - file, http, https, ftp, sftp schemes are supported. 
|                   Use @mib@ placeholder token in URL location to refer
|                   to MIB module name requested.
|        format   - pysnmp format is only supported.


Specifying MIB source
+++++++++++++++++++++

The --mib-source option can be given multiple times. Each instance of
--mib-source must specify a URL where ASN.1 MIB modules should be
looked up and downloaded from. At this moment three MIB sourcing
methods are supported:

* Local files. This could be a top-level directory where MIB files are
  located. Subdirectories will be automatically traversed as well. 
  Example: file:///usr/share/snmp .
* HTTP/HTTPS. A fully specified URL where MIB module name is specified by
  a @mib@ placeholder. When specific MIB is looked up, PySMI will replace
  that placeholder with MIB module name it is looking for. 
  Example: http://mibs.snmplabs.com/asn1/@mib@
* SFTP/FTP. A fully specified URL including FTP username and password. 
  MIB module name is specified by a @mib@ placeholder. When specific MIB
  is looked up, PySMI will replace that placeholder with MIB module name
  it is looking for.  Example: http://mibs.snmplabs.com/asn1/@mib@

When trying to fetch a MIB module, the mibdump tool will try each of
configured --mib-source transports in order of specification till 
first successful hit.

By default mibdump will search:

* file:///usr/share/snmp
* http://mibs.snmplabs.com/asn1/@mib@

Once another --mib-source option is given, those defaults will not be used
and should be manually given to mibdump if needed.

Fuzzying MIB module names
+++++++++++++++++++++++++

There is no single convention on how MIB module files should be named. By
default mibdump will try a handful of guesses when trying to find a file
containing specific MIB module. It will try upper and lower cases, a file 
named after MIB module, try adding different extensions to a file (.mib,
.my etc), try adding/cutting the '-MIB' part of the file name.
If nothing matches, mibdump will consider that probed --mib-source
does not contain MIB module it is looking for.

There is a small chance, though, that fuzzy natching may result in getting
a wrong MIB. If that happens, you can disable the above fuzzyness by
giving mibdump the --disable-fuzzy-source flag.

Avoiding excessive transformation
+++++++++++++++++++++++++++++++++

It well may happen that many MIB modules refer to a common single MIB
module. In that case mibdump may transform it many times unless you
tell mibdump where to search for already transformed MIBs. That place
could of course be a directory where mibdump writes its transforms into
and/or some other local locations.

The --mib-searcher option specifies either local directory or importable
Python package (applicable to pysnmp transformation) containing transformed
MIB modules. Multiple --mib-searcher options could be given, mibdump
will use each of them in oroder of specification till first hit.

If no transformed MIB module is found, mibdump will go on running its full
transformation cycle.

By default mibdump will use:

* --mib-searcher=$HOME/.pysnmp/mibs
* --mib-searcher=pysnmp_mibs

Once another --mib-searcher option is given, those defaults will not be used
and should be manually given to mibdump if needed.

Blacklisting MIBs
+++++++++++++++++

Some MIBs may not be automatically transformed into another form and 
therefore must be explicitly excluded from processing. Such MIBs are
normally manually implemented for each targer MIB format. Examples 
include MIBs containing base SMI types or ASN.1 MACRO definitions
(SNMPv2-SMI, SNMPV2-TC), initially compiled but later manually modified 
MIBs and others.

Default list of blacklisted MIBs for pysnmp transformation target 
is: RFC-1212, RFC-1215, RFC1065-SMI, RFC1155-SMI, RFC1158-MIB, 
RFC1213-MIB, SNMP-FRAMEWORK-MIB, SNMP-TARGET-MIB, SNMPv2-CONF, SNMPv2-SMI,
SNMPv2-TC, SNMPv2-TM, TRANSPORT-ADDRESS-MIB.

If you need to modify this list use the --mib-stub option.

Dealing with broken MIBs
++++++++++++++++++++++++

Curiously enough, some MIBs coming from quite prominent vendors 
appear syntaxically incorrect. That leads to MIB compilers fail on
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


Chosing target transformation
+++++++++++++++++++++++++++++

Although PySMI design allows many transformation formats to be
supported in form of specialized code generation components, the
only target format currently implemented is pysnmp.

Therefore the --destination-format option is pretty much useless
at the moment.

Setting destination directory
+++++++++++++++++++++++++++++

By default mibdump writes transformed MIBs into:

* $HOME/.pysnmp/mibs  (on UNIX)
* @HOME@\PySNMP Configuration\MIBs\  (on Windows)

Use --destination-directory option to change default output
diretory.

Performing unconditional transformation
+++++++++++++++++++++++++++++++++++++++

By default PySMI will avoid creating new transformations if fresh
enough versions already exist. By using --rebuild option you could
trick PySMI doing requested transformation for all given MIB modules.

Ignoring transformation errors
++++++++++++++++++++++++++++++

By default PySMI will stop on first fatal error occurred during
transformations of a series of MIBs. If you wish PySMI to ignore
fatal errors and therefore skipping failed MIB, use the --ignore-errors
option.

Keep in mind that skipping transformation of MIBs that are imported
by other MIBs might make dependant MIBs inconsistent for use.

Skipping dependencies
+++++++++++++++++++++

Most MIBs rely on other MIBs for their operations. This is indicated
by the IMPORT statement in ASN.1 language. PySMI attempts to transform
all MIBs IMPORT'ed by MIB being transformed. That is done in recurrsive
manner.

By using --no-dependencies flag you can tell PySMI not to transform any
MIBs other than those explicitly requested to be transformed.

Keep in mind that skipping dependencies may make the whole set of
transformed MIBs inconsistent.

Generating MIB texts
++++++++++++++++++++

Most MIBs are very verbose. They contain many human-oriented descriptions
and clarifications written in plain English. Those texts may be useful 
for MIB browser applications (to display those texts to human operator)
but might not make any sense in other applications.

To save space and CPU time, PySMI does not by default include those texts 
into transformed MIBs. However this can be reverted by adding
--generate-mib-texts option.

Minor speedups
++++++++++++++

There are a few options that may improve PySMI performance.

The --cache-directory option may be used to point to a temporary
writable directory where PySMI parser (e.g. Ply) would store its 
lookup tables.

By default PySMI performing transformation into pysnmp format will 
also pre-compile Python source into interpreter bytecode. That takes
some time and space. If you wish not to cache Python bytecode
or to do that later, use the --no-python-compile option.

Developer documentation
-----------------------

Running MIB transformation
++++++++++++++++++++++++++

*MibCompiler* class instance should be used for MIB module transformation.

.. autoclass:: pysmi.compiler.MibCompiler
  :members:

MIB Transformation results
++++++++++++++++++++++++++

*MibStatus* class instance is used by :func:`MibCompiler.compiler` to 
indicate the outcome of MIB transformation operation.

.. autoclass:: pysmi.compiler.MibStatus
  :members:

Fetching ASN.1 MIBs
+++++++++++++++++++

PySMI offers three distinct transport mechanisms for fetching MIBs by name
from specific locations. In all cases MIB module name to file name match 
may not be exact -- some name fuzzying can be performed to mitigate 
possible changes to MIB file name.

*FileReader* class instance looks up MIB files in given directories on
the host running PySMI.

.. autoclass:: pysmi.reader.localfile.FileReader
  :members:

*HttpReader* class instance tries to download MIB files using configured URL.

.. autoclass:: pysmi.reader.httpclient.HttpReader
  :members:

*FtpReader* class instance tries to download MIB files form configured FTP server.

.. autoclass:: pysmi.reader.ftpclient.FtpReader
  :members:

Blocking unwanted transformations
+++++++++++++++++++++++++++++++++

There are cases when MIB transformation may or must not be performed.
Such cases include:

* foundation MIBs containing manually implemented pieces or ASN.1 MACRO's
* obsolete MIBs fully reimplemented within modern MIBs
* already transformed MIBs

*MibCompiler* expects user to supply a *searcher* object that would
approve or skip MIB transformation for particular name based on whatever 
reason it is aware of.

In general, *searcher* logic is specific to target format. Here we will
speak solely of pysnmp code generation backend.

Transformed MIBs that were saved in form of Python files can be checked
with *PyFileSearcher* class instances.

.. autoclass:: pysmi.searcher.pyfile.PyFileSearcher
  :members:

Some MIBs, most frequently the base ones, can be stored at a Python package.
There existence can be checked with the *PyPackageSearcher* class instances.

.. autoclass:: pysmi.searcher.pypackage.PyPackageSearcher
  :members:

Foundation or obsolete MIBs that should never be transformed can be
blindly excluded by listing their names at the *StubSearcher* class
instance.

.. autoclass:: pysmi.searcher.stub.StubSearcher
  :members:

A pysnmp-specific list of MIB names to be permanently excluded from
transformation can be found at :py:const:`pysmi.codegen.pysnmp.baseMibs`.

Tackling MIB parser
+++++++++++++++++++

SNMP MIBs are written in two kinds of special language - SMIv1 and SMIv2.
The first SMI version is obsolete, most MIBs by now are written in SMIv2
grammar. There are also efforts aimed at improving SMIv2, but those MIBs
are in great minority at the time of this writing.

PySMI is designed to handle both SMIv1 and SMIv2. The way it is done is
that SMIv2 is considered the most basic and complete, whereas SMIv1 is a
specialization of SMIv2 syntax.

For a user to acqure SMIv2 parser the following factory function should
be used.

.. autofunction:: pysmi.parser.smi.parserFactory

PySMI offers a pre-built collection of parser grammar relaxation options
to simplify its use.

>>> from pysmi.parser.dialect import smiV1
>>> from pysmi.parser.smi import parserFactory
>>> SmiV1Parser = parserFactory(**smiV1)

Apparently, many production MIBs were shipped in syntaxically broken
condition. PySMI attempts to work around such issues by allowing some
extra SMI grammar relaxations. You can enable all those relaxations at
once to maximize the number of MIBs, found in the wild, successfully
compiled.

>>> from pysmi.parser.dialect import smiV1Relaxed
>>> from pysmi.parser.smi import parserFactory
>>> RelaxedSmiV1Parser = parserFactory(**smiV1Relaxed)

.. tip:: Please, note that *parserFactory* function returns a class, not
         class instance. Make sure to instantiate it when passing to
         *MibCompiler* class constructor.

Defining target transformation
++++++++++++++++++++++++++++++

PySMI is designed to be able to transform ASN.1 MIBs into many different
forms. Destination MIB representation is determined by a kind of 
*code generator* object being passed to *MibCompiler* on instantiation.

At the time of this writing, a single fully functional code generation
backend is shipped with PySMI.

.. autoclass:: pysmi.codegen.pysnmp.PySnmpCodeGen
  :members:
  
.. autoclass:: pysmi.codegen.null.NullCodeGen
  :members:

Borrowing pre-transformed MIBs
++++++++++++++++++++++++++++++

Some shipped MIBs appear broken beyond automatic repair. To handle such
cases PySMI introduces the 'borrowing' functionality -- *MibCompiler*
ability to go out and take a copy of already transformed MIB from some
repository.

This feature is optional so it is user responsibility to configure one or
more borrowing objects to *MibCompiler*.

.. autoclass:: pysmi.borrower.pyfile.PyFileBorrower
  :members:

Storing transformed MIBs
++++++++++++++++++++++++

Successfully transformed MIB modules' contents will be passed to *writer*
object given to *MibCompiler* on instantiation. Current version of PySMI
is shipped with the following *writer* classes.

.. autoclass:: pysmi.writer.pyfile.PyFileWriter
  :members:

.. autoclass:: pysmi.writer.callback.CallbackWriter
  :members:

Hints and tricks
----------------

The PySMI project developers maintain a collection of ASN.1 MIB files
at http://mibs.snmplabs.com/asn1/ . The *mibdump* tool as well as many
other utilities based on PySMI are programmed to use this MIB
repository for automatic download and dependency resolution.

You can always reconfigure PySMI to use some other remote MIB repository
instead or in addition to this one.

Should you have any questions or feedback on PySMI software, you are
welcome to ping me at ilya@glas.net .

License
-------

Copyright (c) 2015 Ilya Etingof <ilya@glas.net>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, 
  this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE. 

