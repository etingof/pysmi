
.. _searcher.stub.StubSearcher:

Unconditionally ignore MIBs
---------------------------

Foundation or obsolete MIBs that should never be transformed can be
blindly excluded by listing their names at the *StubSearcher* class
instance.

.. autoclass:: pysmi.searcher.stub.StubSearcher
   :members:

   .. note::

      A pysnmp-specific list of MIB names to be permanently excluded from
      transformation can be found at :py:const:`pysmi.codegen.pysnmp.baseMibs`.
