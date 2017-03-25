
PySMI documentation
===================

.. toctree::
   :maxdepth: 2

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

The library is shipped with a command-line tool called mibdump.py
that utilizes most of PySMI library features. Most importantly,
it allows you to convert ASN.1 MIBs into PySNMP format.

   .. toctree::
      :maxdepth: 2

      /user-perspective

Developer documentation
-----------------------

Whenever you wish to build SNMP MIB parsing functionality into your
Python application, PySMI may be helpful. The following section describes
PySMI programming interfaces and provides code snippets explaining its use.

   .. toctree::
      :maxdepth: 2

      /developer-documentation

Hints and tricks
----------------

The PySMI project developers maintain a collection of ASN.1 MIB files
at http://mibs.snmplabs.com/asn1/ . The *mibdump* tool as well as many
other utilities based on PySMI are programmed to use this MIB
repository for automatic download and dependency resolution.

You can always reconfigure PySMI to use some other remote MIB repository
instead or in addition to this one.

Should you have any questions or feedback on PySMI software, you are
welcome to ping me at etingof@gmail.com .

License
-------

.. include:: ../../LICENSE.rst
