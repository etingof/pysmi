from pysmi.lexer.smiv1 import SmiV1Lexer 
from pysmi.parser.smiv2 import SmiV2Parser
from pysmi import error
from pysmi import debug

class SmiV1Parser(SmiV2Parser):
  defaultLexer = SmiV1Lexer

  #
  # SMIv1 grammar follows
  #

  # NETWORKADDRESS added
  def p_importedKeyword(self, p): 
    """importedKeyword : importedSMIKeyword
                       | BITS
                       | INTEGER32
                       | IPADDRESS
                       | NETWORKADDRESS
                       | MANDATORY_GROUPS
                       | MODULE_COMPLIANCE
                       | MODULE_IDENTITY
                       | OBJECT_GROUP
                       | OBJECT_IDENTITY
                       | OBJECT_TYPE
                       | OPAQUE
                       | TEXTUAL_CONVENTION
                       | TIMETICKS
                       | UNSIGNED32"""
    p[0] = p[1]

  # NETWORKADDRESS added
  def p_typeSMIandSPPI(self, p):
    """typeSMIandSPPI : IPADDRESS
                      | NETWORKADDRESS
                      | TIMETICKS
                      | OPAQUE
                      | INTEGER32
                      | UNSIGNED32"""
    p[0] = p[1]

  # NETWORKADDRESS added
  def p_ApplicationSyntax(self, p):
    """ApplicationSyntax : IPADDRESS anySubType
                         | NETWORKADDRESS anySubType
                         | COUNTER32
                         | COUNTER32 integerSubType
                         | GAUGE32
                         | GAUGE32 integerSubType
                         | UNSIGNED32
                         | UNSIGNED32 integerSubType
                         | TIMETICKS anySubType
                         | OPAQUE
                         | OPAQUE octetStringSubType
                         | COUNTER64
                         | COUNTER64 integerSubType"""
    n = len(p)
    if n == 2:                                                                  
      p[0] = ('ApplicationSyntax', p[1])                                        
    elif n == 3:
      p[0] = ('ApplicationSyntax', p[1], p[2])

  # SMIv1 IndexTypes added
  def p_Index(self, p):
    """Index : ObjectName
             | typeSMIv1"""
               
    # libsmi: TODO: use the SYNTAX value of the correspondent 
    #               OBJECT-TYPE invocation
    p[0] = isinstance(p[1], tuple) and p[1][1][0] or p[1]

  # for Index rule
  def p_typeSMIv1(self, p):
    """typeSMIv1 : INTEGER
                 | OCTET STRING
                 | IPADDRESS
                 | NETWORKADDRESS"""
    n = len(p)
    indextype = n == 3 and p[1] + ' ' + p[2] or p[1]
    p[0] = indextype

  # NETWORKADDRESS added for SEQUENCE syntax
  def p_sequenceApplicationSyntax(self, p):
    """sequenceApplicationSyntax : IPADDRESS anySubType
                                 | NETWORKADDRESS anySubType
                                 | COUNTER32 anySubType
                                 | GAUGE32 anySubType
                                 | UNSIGNED32 anySubType
                                 | TIMETICKS anySubType
                                 | OPAQUE
                                 | COUNTER64 anySubType"""
    n = len(p)
    if n == 2:
      p[0] = p[1]
    elif n == 3:
      p[0] = p[1] # XXX not supporting subtypes here
