import re
import ply.lex as lex
from pysmi.lexer.smiv1 import SmiV1Lexer
from pysmi import error
from pysmi import debug

class SmiV1CompatLexer(SmiV1Lexer):
  pass
### Do not overload single lexer methods - overload all or none of them!
