import re
import ply.lex as lex
from pysmi.lexer.smiv2 import SmiV2Lexer
from pysmi import error
from pysmi import debug

class SmiV1Lexer(SmiV2Lexer):
  reserved_words = [
    'ACCESS', 'AGENT-CAPABILITIES', 'APPLICATION', 'AUGMENTS', 'BEGIN', 'BITS',
    'CONTACT-INFO', 'CREATION-REQUIRES', 'Counter', 'Counter32', 'Counter64', 
    'DEFINITIONS', 'DEFVAL', 'DESCRIPTION', 'DISPLAY-HINT', 'END', 'ENTERPRISE',
    'EXTENDS', 'FROM', 'GROUP', 'Gauge', 'Gauge32', 'IDENTIFIER', 'IMPLICIT', 
    'IMPLIED', 'IMPORTS', 'INCLUDES', 'INDEX', 'INSTALL-ERRORS', 'INTEGER', 
    'Integer32', 'IpAddress', 'LAST-UPDATED', 'MANDATORY-GROUPS', 
    'MAX-ACCESS', 'MIN-ACCESS', 'MODULE', 'MODULE-COMPLIANCE', 'MAX',
    'MODULE-IDENTITY', 'NetworkAddress', 'NOTIFICATION-GROUP', 
    'NOTIFICATION-TYPE', 'NOTIFICATIONS', 'OBJECT', 'OBJECT-GROUP',
    'OBJECT-IDENTITY', 'OBJECT-TYPE', 'OBJECTS', 'OCTET', 'OF', 'ORGANIZATION',
    'Opaque', 'PIB-ACCESS', 'PIB-DEFINITIONS', 'PIB-INDEX', 'PIB-MIN-ACCESS',
    'PIB-REFERENCES', 'PIB-TAG', 'POLICY-ACCESS', 'PRODUCT-RELEASE',
    'REFERENCE', 'REVISION', 'SEQUENCE', 'SIZE', 'STATUS', 'STRING',
    'SUBJECT-CATEGORIES', 'SUPPORTS', 'SYNTAX', 'TEXTUAL-CONVENTION', 
    'TimeTicks', 'TRAP-TYPE', 'UNIQUENESS', 'UNITS', 'UNIVERSAL', 'Unsigned32',
    'VALUE', 'VARIABLES', 'VARIATION', 'WRITE-SYNTAX'   
  ]
  
  reserved = {}
  for w in reserved_words:
    reserved[w] = w.replace('-', '_').upper()
    # hack to support SMIv1
    if w == 'Counter':
      reserved[w] = 'COUNTER32'
    elif w == 'Gauge':
      reserved[w] = 'GAUGE32'

  forbidden_words = [
    'ABSENT', 'ANY', 'BIT', 'BOOLEAN', 'BY', 'COMPONENT', 'COMPONENTS',
    'DEFAULT', 'DEFINED', 'ENUMERATED', 'EXPLICIT', 'EXTERNAL', 'FALSE',
    'MIN', 'MINUS-INFINITY', 'NULL', 'OPTIONAL', 'PLUS-INFINITY', 'PRESENT',
    'PRIVATE', 'REAL', 'SET', 'TAGS', 'TRUE', 'WITH'
  ]

  # Token names required!
  tokens = list(set([
    'BIN_STRING',
    'CHOICE',
    'COLON_COLON_EQUAL',
    'DOT_DOT',
    'EXPORTS',
    'HEX_STRING',
    'LOWERCASE_IDENTIFIER',
    'MACRO',
    'NEGATIVENUMBER',
    'NEGATIVENUMBER64',
    'NUMBER',
    'NUMBER64',
    'QUOTED_STRING',
    'UPPERCASE_IDENTIFIER',
  ] + list(reserved.values())
  ))

### Do not overload single lexer methods - overload all or none of them!
