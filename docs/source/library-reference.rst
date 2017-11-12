
PySMI library
=============

The *MibCompiler* object is the top-most interface to PySMI library features.
It holds together the otherwise isolated pieces of the compiler infrastructure
and manages the workflow of ASN.1 MIB transformation.

This example showcases most of its features:

.. code-block:: python

   from pysmi.reader import FileReader, HttpReader
   from pysmi.searcher import StubSearcher
   from pysmi.writer import CallbackWriter
   from pysmi.parser import SmiStarParser
   from pysmi.codegen import JsonCodeGen
   from pysmi.compiler import MibCompiler

   inputMibs = ['IF-MIB', 'IP-MIB']

   srcDirectories = ['/usr/share/snmp/mibs']
   httpSources = [('mibs.snmplabs.com', 80, '/asn1/@mib@')]

   # store compiled MIBs by calling this function
   def store_mibs(mibName, jsonDoc, cbCtx):
       print('# MIB module %s' % mibName)
       print(jsonDoc)

   mibCompiler = MibCompiler(
       SmiStarParser(), JsonCodeGen(), CallbackWriter(store_mibs)
   )

   # pull ASN.1 MIBs from these locations
   mibCompiler.addSources(*[FileReader(x) for x in srcDirectories])
   mibCompiler.addSources(*[HttpReader(*x) for x in httpSources])

   # never recompile MIBs with ASN.1 MACROs
   mibCompiler.addSearchers(StubSearcher(*JsonCodeGen.baseMibs))

   status = mibCompiler.compile(*inputMibs)

   print(status)

.. toctree::
   :maxdepth: 2

   /pysmi/compiler/mibcompiler
   /pysmi/compiler/mibstatus

MIB sources
-----------

PySMI offers a handful of distinct transport mechanisms for fetching MIBs by
name from specific locations. In all cases MIB module name to file name match
may not be exact -- some name fuzzying can be performed to mitigate
possible changes to MIB file name.

.. toctree::
   :maxdepth: 2

   /pysmi/reader/localfile/filereader
   /pysmi/reader/zipreader/zipreader
   /pysmi/reader/httpclient/httpreader
   /pysmi/reader/ftpclient/ftpreader
   /pysmi/reader/callback/callbackreader

Conditional compilation
-----------------------

There are cases when MIB transformation may or must not be performed.
Such cases include:

* foundation MIBs containing manually implemented pieces or ASN.1 MACRO's
* obsolete MIBs fully reimplemented within modern MIBs
* already transformed MIBs

:ref:`MibCompiler <compiler.MibCompiler>` expects user to supply a
*searcher* object that would allow or skip MIB transformation for particular
name based on whatever reason it is aware of.

In general, *searcher* logic is specific to target format. At the time being,
only `pysnmp <http://snmplabs.com/pysnmp>`_ code generation backend requires
such filtering.

.. toctree::
   :maxdepth: 2

   /pysmi/searcher/pyfile/pyfilesearcher
   /pysmi/searcher/pypackage/pypackagesearcher
   /pysmi/searcher/stub/stubsearcher

Parser configuration
--------------------

MIBs may be written in one of the two major SMI language versions (v1 and v2).
Some MIBs may contain typical errors.

PySMI offers a way to customize the parser to consume either of the major SMI
grammars as well as to recover from well-known errors in MIB files.

.. toctree::
   :maxdepth: 2

   /pysmi/parser/smi/parserfactory
   /pysmi/parser/smi/dialect

Code generators
---------------

Once ASN.1 MIB is parsed up, AST is passed to a code generator which turns
AST into desired representation of the MIB.

.. toctree::
   :maxdepth: 2

   /pysmi/codegen/jsondoc/jsoncodegen
   /pysmi/codegen/pysnmp/pysnmpcodegen
   /pysmi/codegen/null/nullcodegen

Borrow pre-compiled MIBs
------------------------

Some MIBs in circulation appear broken beyond automatic repair. To
handle such cases PySMI introduces the *MIB borrowing*
functionality. When :ref:`MibCompiler <compiler.MibCompiler>`
gives up compiling a MIB, it can try to go out and take a copy of
already transformed MIB to complete the request successfully.

.. toctree::
   :maxdepth: 2

   /pysmi/borrower/anyfile/anyfileborrower
   /pysmi/borrower/pyfile/pyfileborrower

Write compiled MIBs
-------------------

Successfully transformed MIB modules' contents will be passed to *writer*
object given to :ref:`MibCompiler <compiler.MibCompiler>` on instantiation.

.. toctree::
   :maxdepth: 2

   /pysmi/writer/localfile/filewriter
   /pysmi/writer/pyfile/pyfilewriter
   /pysmi/writer/callback/callbackwriter
