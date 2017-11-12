
.. _parser.smi.dialect:

SMI language dialects
---------------------

PySMI offers a pre-built collection of parser grammar relaxation options
to simplify its use:

* *pysmi.parser.dialect.smiV2* - canonical SMIv2 grammar
* *pysmi.parser.dialect.smiV1* - canonical SMIv1 grammar
* *pysmi.parser.dialect.smiV1Relaxed* - relaxed SMIv1 grammar allowing some deviations

The grammar object should be passed to the :ref:`parserFactory <parser.smi.parserFactory>` function.

.. code-block:: python

  from pysmi.parser.dialect import smiV1
  from pysmi.parser.smi import parserFactory

  SmiV1Parser = parserFactory(**smiV1)

Apparently, many production MIBs were shipped in syntactically broken
condition. PySMI attempts to work around such issues by allowing some
extra SMI grammar relaxations. You can enable all those relaxations at
once to maximize the number of MIBs, found in the wild, successfully
compiled.

.. code-block:: python

  from pysmi.parser.dialect import smiV1Relaxed
  from pysmi.parser.smi import parserFactory

  RelaxedSmiV1Parser = parserFactory(**smiV1Relaxed)
