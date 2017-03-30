Revision 0.1.1, 30-03-2017
--------------------------

* Generate REFERENCE and STATUS fields at various SMI objects
* Generate DESCRIPTION field followed REVISION field at MODULE-IDENTITY objects
* Generate PRODUCT-RELEASE field at AGENT-CAPABILITIES objects
* Generated Python source aligned with PEP8
* MIB texts cleaned up by default, --keep-texts-layout preserves original formatting
* Fix to the `ordereddict` conditional dependency
* Missing test module recovered
* Failing tests fixed

Revision 0.1.0, 25-03-2017
--------------------------

* JSON code generating backend implemented
* Experimental JSON OID->MIB indices generation implemented
* Package structure flattened for easier use
* Minor refactoring to the test suite
* Source code statically analyzed, hardened and PEP8-ized
* Files closed explicitly to mute ResourceWarnings
* Fixed to Python 2.4 (and aged ply) compatibility
* Added a workaround to avoid generating pysnmp TextualConvention classes
  inheriting from TextualConvention (when MIB defines a TEXTUAL-CONVENTION
  based on another TEXTUAL-CONVENTION as SYNTAX)
* Author's e-mail changed, copyright extended to year 2017

Revision 0.0.7, 12-02-2016
--------------------------

* Crash on existing .py file handling fixed.
* Fix to __doc__ use in setup.py to make -O0 installation mode working.
* Fix to PyPackageSearcher not to fail on broken Python packages.
* Source code pep8'ed
* Copyright added to source files.

Revision 0.0.6, 01-10-2015
--------------------------

* Several typos fixed, source code linted again.
* Some dead code cleaned up.

Revision 0.0.5, 28-09-2015
--------------------------

* Wheel distribution format now supported.
* Handle the case of MIB symbols conflict with Python reserved words.
* Handle binary DEFVAL initializer for INTEGER's.
* Generate LAST-UPDATED at pysnmp code generator.

Revision 0.0.4, 01-07-2015
--------------------------

* Fix to MRO compliance for mixin classes generation at pysnmp backend
* Fix to repeated imports in generated code at pysnmp backend
* Fix to mibdump tool to properly handle the --generate-mib-texts option.
* Fix to Python compile() - optimize flag is valid only past Python 3.1
* Fix to SMIv1 INDEX clause code generation for pysnmp backend.
* Tighten file creation security at pysmi.writer.pyfile

Revision 0.0.3, 28-06-2015
--------------------------

* Two-pass compiler design allows for much accurate code generation.
* Sphinx-based documentation first introduced

Revision 0.0.0, 11-04-2015
--------------------------

* First public release, not fully operational yet
