import inspect
import os
import sys
import ply.yacc as yacc
from pysmi.lexer.smiv1compat import SmiV1CompatLexer
from pysmi.parser.smiv1 import SmiV1Parser
from pysmi import error
from pysmi import debug

class SmiV1CompatParser(SmiV1Parser):
  defaultLexer = SmiV1CompatLexer
  #
  # Some changes in grammar to handle common mistakes in MIBs 
  #

  # common typos handled 
  def p_sequenceItems(self, p):
    """sequenceItems : sequenceItems ',' sequenceItem
                     | sequenceItem
                     | sequenceItems ','""" 
    # libsmi: TODO: might this list be emtpy?
    n = len(p)
    if n == 4:
      p[0] = p[1] + [p[3]]
    elif n == 2:
      p[0] = [p[1]]
    elif n == 3: # typo case
      p[0] = p[1]

  # common typos handled (mix of commas and spaces)
  def p_enumItems(self, p):
    """enumItems : enumItems ',' enumItem
                 | enumItem
                 | enumItems enumItem
                 | enumItems ','"""
    n = len(p)
    if n == 4:
      p[0] = p[1] + [p[3]]
    elif n == 2:
      p[0] = [p[1]]
    elif n == 3: # typo case
      if p[2] == ',':
        p[0] = p[1]
      else:
        p[0] = p[1] + [p[2]]

  # common mistake - using UPPERCASE_IDENTIFIER
  def p_enumItem(self, p):
    """enumItem : LOWERCASE_IDENTIFIER '(' enumNumber ')'
                | UPPERCASE_IDENTIFIER '(' enumNumber ')'"""
    p[0] = (p[1], p[3])

  # common mistake - LOWERCASE_IDENTIFIER in symbol's name
  def p_notificationTypeClause(self, p):
    """notificationTypeClause : fuzzy_lowercase_identifier NOTIFICATION_TYPE NotificationObjectsPart STATUS Status DESCRIPTION Text ReferPart COLON_COLON_EQUAL '{' NotificationName '}'""" # some MIBs have uppercase and/or lowercase id
    p[0] = ('notificationTypeClause', p[1], # id
                                    #  p[2], # NOTIFICATION_TYPE
                                      p[3], # NotificationObjectsPart
                                    #  p[5], # status
                                      (p[6], p[7]), # description
                                    #  p[8], # ReferPart
                                      p[11]) # NoficationName aka objectIdentifier

