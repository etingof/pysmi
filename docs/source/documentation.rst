
PySMI documentation
===================

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

The location of ASN.1 MIB modules and flavor of their syntax, as well as
desired transformation format, is determined by respective components
chosen and configured to compiler.

.. toctree::
   :maxdepth: 2

   /mibdump
   /library-reference
