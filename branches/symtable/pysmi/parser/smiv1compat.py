from pysmi.parser.smi import parserFactory
from pysmi.parser.dialect import smiV1Relaxed

# compatibility stub
SmiV1CompatParser = parserFactory(**smiV1Relaxed)
