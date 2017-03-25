PySMI: developer documentation
==============================

The following chapter documents public API of the PySMI library.

.. toctree::
   :maxdepth: 2

Running MIB transformation
--------------------------

*MibCompiler* class instance should be used for MIB module transformation.

.. autoclass:: pysmi.compiler.MibCompiler
  :members:

MIB Transformation results
--------------------------

*MibStatus* class instance is used by :func:`MibCompiler.compiler` to 
indicate the outcome of MIB transformation operation.

.. autoclass:: pysmi.compiler.MibStatus
  :members:

Fetching ASN.1 MIBs
-------------------

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
---------------------------------

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
-------------------

SNMP MIBs are written in two kinds of special language - SMIv1 and SMIv2.
The first SMI version is obsolete, most MIBs by now are written in SMIv2
grammar. There are also efforts aimed at improving SMIv2, but those MIBs
are in great minority at the time of this writing.

PySMI is designed to handle both SMIv1 and SMIv2. The way it is done is
that SMIv2 is considered the most basic and complete, whereas SMIv1 is a
specialization of SMIv2 syntax.

For a user to acquire SMIv2 parser the following factory function should
be used.

.. autofunction:: pysmi.parser.smi.parserFactory

PySMI offers a pre-built collection of parser grammar relaxation options
to simplify its use.

.. code-block:: python

  from pysmi.parser.dialect import smiV1
  from pysmi.parser.smi import parserFactory

  SmiV1Parser = parserFactory(**smiV1)

Apparently, many production MIBs were shipped in syntaxically broken
condition. PySMI attempts to work around such issues by allowing some
extra SMI grammar relaxations. You can enable all those relaxations at
once to maximize the number of MIBs, found in the wild, successfully
compiled.

.. code-block:: python

  from pysmi.parser.dialect import smiV1Relaxed
  from pysmi.parser.smi import parserFactory

  RelaxedSmiV1Parser = parserFactory(**smiV1Relaxed)

.. tip:: Please, note that *parserFactory* function returns a class, not
         class instance. Make sure to instantiate it when passing to
         *MibCompiler* class constructor.

Defining target transformation
------------------------------

PySMI is designed to be able to transform ASN.1 MIBs into many different
forms. Destination MIB representation is determined by a kind of 
*code generator* object being passed to *MibCompiler* on instantiation.

At the time of this writing, two code generation backends are shipped
with PySMI.

.. autoclass:: pysmi.codegen.pysnmp.PySnmpCodeGen
  :members:

.. autoclass:: pysmi.codegen.jsondoc.JsonCodeGen
  :members:

.. autoclass:: pysmi.codegen.null.NullCodeGen
  :members:

Borrowing pre-transformed MIBs
------------------------------

Some shipped MIBs appear broken beyond automatic repair. To handle such
cases PySMI introduces the 'borrowing' functionality -- *MibCompiler*
ability to go out and take a copy of already transformed MIB from some
repository.

This feature is optional so it is user responsibility to configure one or
more borrowing objects to *MibCompiler*.

.. autoclass:: pysmi.borrower.pyfile.PyFileBorrower
  :members:

Storing transformed MIBs
------------------------

Successfully transformed MIB modules' contents will be passed to *writer*
object given to *MibCompiler* on instantiation. Current version of PySMI
is shipped with the following *writer* classes.

.. autoclass:: pysmi.writer.pyfile.PyFileWriter
  :members:

.. autoclass:: pysmi.writer.callback.CallbackWriter
  :members:
