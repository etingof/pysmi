
.. _parser.smi.parserFactory:

SMI parser
----------

SNMP MIBs are written in two kinds of special language - SMIv1 and SMIv2.
The first SMI version is obsolete, most MIBs by now are written in SMIv2
grammar. There are also efforts aimed at improving SMIv2, but those MIBs
are in great minority at the time of this writing.

PySMI is designed to handle both SMIv1 and SMIv2. The way it is done is
that SMIv2 is considered the most basic and complete, whereas SMIv1 is a
specialization of SMIv2 syntax.

For a user to acquire SMIv2 parser the *parserFactory* function should
be called with the :ref:`SMI dialect object <parser.smi.dialect>`.

The parser object should be passed to the :ref:`MibCompiler <compiler.MibCompiler>` object.

.. autofunction:: pysmi.parser.smi.parserFactory

.. note::

   Please, note that *parserFactory* function returns a class, not
   class instance. Make sure to instantiate it when passing to
   :ref:`MibCompiler <compiler.MibCompiler>` class constructor.
