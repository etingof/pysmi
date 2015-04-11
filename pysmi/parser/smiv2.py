import inspect
import ply.yacc as yacc
from pysmi.lexer.smiv2 import SmiV2Lexer 
from pysmi.parser.base import AbstractParser
from pysmi import error
from pysmi import debug

class SmiV2Parser(AbstractParser):
  def __init__(self, startSym='mibFile', tempdir=None):
    self.lexer = SmiV2Lexer()

    # tokens are required for parser
    self.tokens = self.lexer.tokens

    if debug.logger & debug.flagParser:
      logger = debug.logger.getCurrentLogger()
    else:
      logger = yacc.NullLogger()

    self.parser = yacc.yacc(module=self,
                            start=startSym,
                            write_tables=bool(tempdir),
                            debug=False,
                            debuglog=logger,
                            errorlog=logger)

  def parse(self, data, **kwargs):
    debug.logger & debug.flagParser and debug.logger('source MIB size is %s characters, first 50 characters are "%s..."' % (len(data), data[:50]))
    return self.parser.parse(data, lexer=self.lexer.lexer)
#    debug.logger & debug.flagCompiler and debug.logger('required MIB(s): %s, Python code size is %s bytes' % (','.join(othermibs) or '<none>', len(data)))

  #
  # SMIv2 grammar follows
  #

  def p_mibFile(self, p):
    """mibFile : modules
               | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('mibFile', p[1])
    # done

  def p_modules(self, p):
    """modules : modules module
               | module"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 3:
      p[0] = p[1] + [p[2]]
    elif n == 2:
      p[0] = [p[1]]
    # done

  def p_module(self, p):
    """module : moduleName moduleOid definitions COLON_COLON_EQUAL BEGIN exportsClause linkagePart declarationPart END"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = (p[1], # name 
            p[2], # oid
            p[7], # linkage (imports)
            p[8]) # declaration
    # done

  def p_moduleOid(self, p):
    """moduleOid : '{' objectIdentifier '}'
                 | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 4:
      p[0] = p[2]
    # done

  def p_definitions(self, p):
    """definitions : DEFINITIONS
                   | PIB_DEFINITIONS"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    pass

  def p_linkagePart(self, p):
    """linkagePart : linkageClause
                   | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      p[0] = p[1]
    # done

  def p_linkageClause(self, p):
    """linkageClause : IMPORTS importPart ';'"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[2]
    # done

  def p_exportsClause(self, p):
    """exportsClause : EXPORTS
                     | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    pass

  def p_importPart(self, p):
    """importPart : imports
                  | empty"""
    # libsmi: TODO: ``IMPORTS ;'' allowed? refer ASN.1!
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      importDict = {}
      for imp in p[1]: # don't do just dict() because moduleNames may be repeated
        fromModule, symbols = imp
        if fromModule in importDict:
          importDict[fromModule] += symbols
        else:
          importDict[fromModule] = symbols
      p[0] = importDict
    # done

  def p_imports(self, p):
    """imports : imports import
               | import"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 3:
      p[0] = p[1] + [p[2]]
    elif n == 2:
      p[0] = [p[1]]
    # done

  def p_import(self, p):
    """import : importIdentifiers FROM moduleName"""
    # libsmi: TODO: multiple clauses with same moduleName allowed? 
    # I guess so. refer ASN.1!
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = (p[3], # moduleName
            p[1]) # ids
    # done

  def p_importIdentifiers(self, p):
    """importIdentifiers : importIdentifiers ',' importIdentifier
                         | importIdentifier"""
    # libsmi: TODO: might this list list be empty?
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 4:
      p[0] = p[1] + [p[3]]
    elif n == 2:
      p[0] = [p[1]]
    # done

# Note that some named types must not be imported, REF:RFC1902,590 
  def p_importIdentifier(self, p):
    """importIdentifier : LOWERCASE_IDENTIFIER
                        | UPPERCASE_IDENTIFIER
                        | importedKeyword"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1]
    # done

  def p_importedKeyword(self, p):
    """importedKeyword : importedSMIKeyword
                       | BITS
                       | INTEGER32
                       | IPADDRESS
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
#                     | importedSPPIKeyword
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1]
    # done

  def p_importedSMIKeyword(self, p):
    """importedSMIKeyword : AGENT_CAPABILITIES
                          | COUNTER32
                          | COUNTER64
                          | GAUGE32
                          | NOTIFICATION_GROUP
                          | NOTIFICATION_TYPE
                          | TRAP_TYPE"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1]
    # done

#def p_importedSPPIKeyword(self, p):
#  """importedSPPIKeyword : INTEGER64
#                         | UNSIGNED64"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
#  p[0] = p[1]
    # done

  def p_moduleName(self, p):
    """moduleName : UPPERCASE_IDENTIFIER"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1]
    # done

  def p_declarationPart(self, p):
    """declarationPart : declarations
                       | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      p[0] = p[1]
    # done

  def p_declarations(self, p):
    """declarations : declarations declaration
                    | declaration"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 3:
      p[0] = p[1] + [p[2]]
    elif n == 2:
      p[0] = [p[1]] 
    # done

  def p_declaration(self, p):
    """declaration : typeDeclaration
                   | valueDeclaration
                   | objectIdentityClause
                   | objectTypeClause
                   | trapTypeClause
                   | notificationTypeClause
                   | moduleIdentityClause
                   | moduleComplianceClause
                   | objectGroupClause
                   | notificationGroupClause
                   | agentCapabilitiesClause
                   | macroClause"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      p[0] = p[1]
    # done

  def p_macroClause(self, p):
    """macroClause : macroName MACRO END"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    pass

  def p_macroName(self, p):
    """macroName : MODULE_IDENTITY
                 | OBJECT_TYPE
                 | TRAP_TYPE
                 | NOTIFICATION_TYPE
                 | OBJECT_IDENTITY
                 | TEXTUAL_CONVENTION
                 | OBJECT_GROUP
                 | NOTIFICATION_GROUP
                 | MODULE_COMPLIANCE
                 | AGENT_CAPABILITIES"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    pass

  def p_choiceClause(self, p):
    """choiceClause : CHOICE """
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    pass

# libsmi: The only ASN.1 value declarations are for OIDs, REF:RFC1902,491.
  def p_fuzzy_lowercase_identifier(self, p):
    """fuzzy_lowercase_identifier : LOWERCASE_IDENTIFIER
                                  | UPPERCASE_IDENTIFIER"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1] 
    # done

  def p_valueDeclaration(self, p):
    """valueDeclaration : fuzzy_lowercase_identifier OBJECT IDENTIFIER COLON_COLON_EQUAL '{' objectIdentifier '}'"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('valueDeclaration', p[1],              # id
                                p[6])              # objectIdentifier
    
  def p_typeDeclaration(self, p):
    """typeDeclaration : typeName COLON_COLON_EQUAL typeDeclarationRHS"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('typeDeclaration', p[1], # name
                               p[3]) # declarationRHS

  def p_typeName(self, p):
    """typeName : UPPERCASE_IDENTIFIER"""
    #            | typeSMI
    #            | typeSPPIonly"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1]

  def p_typeSMI(self, p):
    """typeSMI : typeSMIandSPPI
               | typeSMIonly"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1]

  def p_typeSMIandSPPI(self, p):
    """typeSMIandSPPI : IPADDRESS
                      | TIMETICKS
                      | OPAQUE
                      | INTEGER32
                      | UNSIGNED32"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1]

  def p_typeSMIonly(self, p):
    """typeSMIonly : COUNTER32
                   | GAUGE32
                   | COUNTER64"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1]  

#def p_typeSPPIonly(self, p):
#  """typeSPPIonly : INTEGER64
#                  | UNSIGNED64"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
#  p[0] = p[1]  

  def p_typeDeclarationRHS(self, p):
    """typeDeclarationRHS : Syntax
                          | TEXTUAL_CONVENTION DisplayPart STATUS Status DESCRIPTION Text ReferPart SYNTAX Syntax
                          | choiceClause"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      if p[1] == 'TEXTUAL-CONVENTION':
        p[0] = ('typeDeclarationRHS', p[2], # display
                                    #  p[4], # status
                                    #  (p[5], p[6]), # description
                                    #  p[7], # reference
                                      p[9]) # syntax 
      else:
        p[0] = ('typeDeclarationRHS', p[1])
    # ignore the choiceClause 
    # done
     
  def p_conceptualTable(self, p):
    """conceptualTable : SEQUENCE OF row"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('conceptualTable', p[3])
    # done

  def p_row(self, p):
    """row : UPPERCASE_IDENTIFIER"""
    # libsmi: TODO: this must be an entryType
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('row', p[1])
    # done

  def p_entryType(self, p):
    """entryType : SEQUENCE '{' sequenceItems '}'"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = (p[1], p[3])
    # done

  def p_sequenceItems(self, p):
    """sequenceItems : sequenceItems ',' sequenceItem
                     | sequenceItem"""
    # libsmi: TODO: might this list be emtpy?
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 4:
      p[0] = p[1] + [p[3]]
    elif n == 2:
      p[0] = [p[1]]
    # done
   
  def p_sequenceItem(self, p):
    """sequenceItem : LOWERCASE_IDENTIFIER sequenceSyntax"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = (p[1], p[2])
    # done

  def p_Syntax(self, p):
    """Syntax : ObjectSyntax
              | BITS '{' NamedBits '}'"""
    # libsmi: TODO: standalone `BITS' ok? seen in RMON2-MIB 
    # libsmi: -> no, it's only allowed in a SEQUENCE {...}
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 2:
      p[0] = p[1]
    elif n == 5:
      p[0] = (p[1], p[3])
   
  def p_sequenceSyntax(self, p):
    """sequenceSyntax : BITS
                      | UPPERCASE_IDENTIFIER anySubType
                      | sequenceObjectSyntax"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1] # no subtype or complex syntax supported
    # done

  def p_NamedBits(self, p):
    """NamedBits : NamedBits ',' NamedBit
                 | NamedBit"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 4:
      p[0] = p[1] + [p[3]]
    elif n == 2:
      p[0] = [p[1]]
    # done

  def p_NamedBit(self, p):
    """NamedBit : LOWERCASE_IDENTIFIER '(' NUMBER ')'"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = (p[1], p[3])
    # done

  def p_objectIdentityClause(self, p):
    """objectIdentityClause : LOWERCASE_IDENTIFIER OBJECT_IDENTITY STATUS Status DESCRIPTION Text ReferPart COLON_COLON_EQUAL '{' objectIdentifier '}'"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('objectIdentityClause', p[1], # id
                                  #  p[2], # OBJECT_IDENTITY 
                                  #  p[4], # status
                                    (p[5], p[6]), # description
                                  #  p[7], # reference
                                    p[10]) # objectIdentifier

  def p_objectTypeClause(self, p):
    """objectTypeClause : LOWERCASE_IDENTIFIER OBJECT_TYPE SYNTAX Syntax UnitsPart MaxOrPIBAccessPart SPPIPibReferencesPart SPPIPibTagPart STATUS Status descriptionClause SPPIErrorsPart ReferPart IndexPart MibIndex SPPIUniquePart DefValPart COLON_COLON_EQUAL '{' ObjectName '}'"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('objectTypeClause', p[1], # id
                              #  p[2], # OBJECT_TYPE
                                p[4], # syntax
                                p[5], # UnitsPart
                                p[6], # MaxOrPIBAccessPart
                              #  p[10], # status
                                p[11], # descriptionClause
                              #  p[13], # reference
                                p[14], # augmentions
                                p[15], # index
                                p[17], # DefValPart
                                p[20]) # ObjectName

  def p_descriptionClause(self, p):
    """descriptionClause : DESCRIPTION Text
                         | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      p[0] = (p[1], p[2])
    # done

  def p_trapTypeClause(self, p):
    """trapTypeClause : fuzzy_lowercase_identifier TRAP_TYPE ENTERPRISE objectIdentifier VarPart DescrPart ReferPart COLON_COLON_EQUAL NUMBER"""
    # libsmi: TODO: range of number?
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('trapTypeClause', p[1], # fuzzy_lowercase_identifier
                            #  p[2], # TRAP_TYPE
                              p[4], # objectIdentifier
                              p[5], # VarPart
                              p[6], # description
                            #  p[7], # reference
                              p[9]) # NUMBER

  def p_VarPart(self, p):
    """VarPart : VARIABLES '{' VarTypes '}'
               | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1] and p[3] or []
    # done

  def p_VarTypes(self, p):
    """VarTypes : VarTypes ',' VarType
                | VarType"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 4:
      p[0] = ('VarTypes', p[1][1] + [p[3]])
    elif n == 2:
      p[0] = ('VarTypes', [p[1]])
    # done

  def p_VarType(self, p):
    """VarType : ObjectName"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1][1][0]
    # done

  def p_DescrPart(self, p):
    """DescrPart : DESCRIPTION Text
                 | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      p[0] = (p[1], p[2])

  def p_MaxOrPIBAccessPart(self, p):
    """MaxOrPIBAccessPart : MaxAccessPart
                          | empty"""
    #                      | PibAccessPart
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      p[0] = p[1]
    # done

  def p_PibAccessPart(self, p):
    """PibAccessPart : PibAccess Access"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    #p[0] = (p[1], p[2])
    pass

  def p_PibAccess(self, p):
    """PibAccess : POLICY_ACCESS
                 | PIB_ACCESS"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    #p[0] = p[1]
    pass

  def p_SPPIPibReferencesPart(self, p):
    """SPPIPibReferencesPart : PIB_REFERENCES '{' Entry '}'
                             | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    pass

  def p_SPPIPibTagPart(self, p):
    """SPPIPibTagPart : PIB_TAG '{' ObjectName '}'
                      | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    pass

  def p_SPPIUniquePart(self, p):
    """SPPIUniquePart : UNIQUENESS '{' UniqueTypesPart '}'
                      | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    pass

  def p_UniqueTypesPart(self, p):
    """UniqueTypesPart : UniqueTypes
                       | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    pass

  def p_UniqueTypes(self, p):
    """UniqueTypes : UniqueTypes ',' UniqueType
                   | UniqueType"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    pass

  def p_UniqueType(self, p):
    """UniqueType : ObjectName"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    pass

  def p_SPPIErrorsPart(self, p):
    """SPPIErrorsPart : INSTALL_ERRORS '{' Errors '}'
                      | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    pass

  def p_Errors(self, p):
    """Errors : Errors ',' Error
              | Error"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    pass

  def p_Error(self, p):
    """Error : LOWERCASE_IDENTIFIER '(' NUMBER ')'"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    pass

  def p_MaxAccessPart(self, p):
    """MaxAccessPart : MAX_ACCESS Access
                     | ACCESS Access"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('MaxAccessPart', p[2])
    # done

  def p_notificationTypeClause(self, p):
    """notificationTypeClause : LOWERCASE_IDENTIFIER NOTIFICATION_TYPE NotificationObjectsPart STATUS Status DESCRIPTION Text ReferPart COLON_COLON_EQUAL '{' NotificationName '}'"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('notificationTypeClause', p[1], # id
                                    #  p[2], # NOTIFICATION_TYPE
                                      p[3], # NotificationObjectsPart
                                    #  p[5], # status
                                      (p[6], p[7]), # description
                                    #  p[8], # ReferPart
                                      p[11]) # NoficationName aka objectIdentifier

  def p_moduleIdentityClause(self, p): 
    """moduleIdentityClause : LOWERCASE_IDENTIFIER MODULE_IDENTITY SubjectCategoriesPart LAST_UPDATED ExtUTCTime ORGANIZATION Text CONTACT_INFO Text DESCRIPTION Text RevisionPart COLON_COLON_EQUAL '{' objectIdentifier '}'"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('moduleIdentityClause', p[1], # id
                                  #  p[2], # MODULE_IDENTITY
                                  # XXX  p[3], # SubjectCategoriesPart
                                  #  (p[4], p[5]), # last updated
                                    (p[6], p[7]), # organization
                                    (p[8], p[9]), # contact info
                                    (p[10], p[11]), # description
                                    p[12], # RevisionPart
                                    p[15]) # objectIdentifier
    # done

  def p_SubjectCategoriesPart(self, p):
    """SubjectCategoriesPart : SUBJECT_CATEGORIES '{' SubjectCategories '}'
                             | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    #if p[1]:
    #  p[0] = (p[1], p[3])
    pass

  def p_SubjectCategories(self, p):
    """SubjectCategories : CategoryIDs"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    #p[0] = p[1]
    pass

  def p_CategoryIDs(self, p):
    """CategoryIDs : CategoryIDs ',' CategoryID
                   | CategoryID"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    #n = len(p)
    #if n == 4:
    #  p[0] = ('CategoryIDs', p[1][1] + [p[3]])
    #elif n == 2:
    #  p[0] = ('CategoryIDs', [p[1]])
    pass

  def p_CategoryID(self, p):
    """CategoryID : LOWERCASE_IDENTIFIER '(' NUMBER ')'
                  | LOWERCASE_IDENTIFIER"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    #n = len(p)
    #if n == 2:
    #  p[0] = ('CategoryID', p[1])
    #elif n == 5:
    #  p[0] = ('CategoryID', p[3])
    pass

  def p_ObjectSyntax(self, p):
    """ObjectSyntax : SimpleSyntax
                    | conceptualTable
                    | row
                    | entryType
                    | ApplicationSyntax"""
    #                | typeTag SimpleSyntax
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1]

  def p_typeTag(self, p):
    """typeTag : '[' APPLICATION NUMBER ']' IMPLICIT
               | '[' UNIVERSAL NUMBER ']' IMPLICIT"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    #p[0] = ('typeTag', p[2])
    pass

  def p_sequenceObjectSyntax(self, p):
    """sequenceObjectSyntax : sequenceSimpleSyntax
                            | sequenceApplicationSyntax"""
    # libsmi: TO DO: add to this rule conceptualTable, row, entryType
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1]
    # done 

  def p_valueofObjectSyntax(self, p):
    """valueofObjectSyntax : valueofSimpleSyntax"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1]

  def p_SimpleSyntax(self, p):
    """SimpleSyntax : INTEGER
                    | INTEGER integerSubType
                    | INTEGER enumSpec
                    | INTEGER32
                    | INTEGER32 integerSubType
                    | UPPERCASE_IDENTIFIER enumSpec
                    | UPPERCASE_IDENTIFIER integerSubType
                    | OCTET STRING
                    | OCTET STRING octetStringSubType
                    | UPPERCASE_IDENTIFIER octetStringSubType
                    | OBJECT IDENTIFIER anySubType"""
    #                | moduleName '.' UPPERCASE_IDENTIFIER enumSpec 
    #                | moduleName '.' UPPERCASE_IDENTIFIER integerSubType  
    #                | moduleName '.' UPPERCASE_IDENTIFIER octetStringSubType
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 2:
      p[0] = ('SimpleSyntax', p[1])
    elif n == 3:
      if p[1] == 'OCTET':
        p[0] = ('SimpleSyntax', p[1] + ' ' + p[2])
      else:
        p[0] = ('SimpleSyntax', p[1], p[2])
    elif n == 4:
      p[0] = ('SimpleSyntax', p[1] + ' ' + p[2], p[3])
    #elif n == 5:
    #  p[0] = ('SimpleSyntax', p[1], # moduleName
    #                          p[3], # id
    #                          p[4]) # subtype  

  def p_valueofSimpleSyntax(self, p):
    """valueofSimpleSyntax : NUMBER
                           | NEGATIVENUMBER
                           | NUMBER64
                           | NEGATIVENUMBER64
                           | HEX_STRING
                           | BIN_STRING
                           | LOWERCASE_IDENTIFIER
                           | QUOTED_STRING
                           | '{' objectIdentifier_defval '}'"""
    # libsmi for objectIdentifier_defval:
    # This is only for some MIBs with invalid numerical
    # OID notation for DEFVALs. We DO NOT parse them
    # correctly. We just don't want to produce a
    # parser error.
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 2:
      p[0] = p[1]
    elif n == 4: # XXX
      pass 
    # done

  def p_sequenceSimpleSyntax(self, p):
    """sequenceSimpleSyntax : INTEGER anySubType
                            | INTEGER32 anySubType
                            | OCTET STRING anySubType
                            | OBJECT IDENTIFIER anySubType"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 3:
      p[0] = p[1] # XXX not supporting subtypes here 
    elif n == 4:
      p[0] = p[1] + ' ' + p[2] # XXX not supporting subtypes here
    # done

  def p_ApplicationSyntax(self, p):
    """ApplicationSyntax : IPADDRESS anySubType
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
    #                     | INTEGER64
    #                     | INTEGER64 integerSubType
    #                     | UNSIGNED64
    #                     | UNSIGNED64 integerSubType
    # COUNTER32 and COUNTER64 was with anySubType in libsmi
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 2:
      p[0] = ('ApplicationSyntax', p[1])
    elif n == 3:
      p[0] = ('ApplicationSyntax', p[1], p[2])
    # done

  def p_sequenceApplicationSyntax(self, p):
    """sequenceApplicationSyntax : IPADDRESS anySubType
                                 | COUNTER32 anySubType
                                 | GAUGE32 anySubType
                                 | UNSIGNED32 anySubType
                                 | TIMETICKS anySubType
                                 | OPAQUE
                                 | COUNTER64 anySubType"""
    #                             | INTEGER64
    #                             | UNSIGNED64
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 2:
      p[0] = p[1]
    elif n == 3:
      p[0] = p[1] # XXX not supporting subtypes here
    # done 

  def p_anySubType(self, p):
    """anySubType : integerSubType
                  | octetStringSubType
                  | enumSpec
                  | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      p[0] = p[1]
   
  def p_integerSubType(self, p):
    """integerSubType : '(' ranges ')'"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('integerSubType', p[2])

  def p_octetStringSubType(self, p):
    """octetStringSubType : '(' SIZE '(' ranges ')' ')'"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('octetStringSubType', p[4])

  def p_ranges(self, p):
    """ranges : ranges '|' range
              | range"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 4:
      p[0] = p[1] + [p[3]]
    elif n == 2:
      p[0] = [p[1]]
    # done
   
  def p_range(self, p):
    """range : value DOT_DOT value
             | value"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 2:
      p[0] = (p[1],)
    elif n == 4:
      p[0] = (p[1], p[3])
    # done

  def p_value(self, p):
    """value : NEGATIVENUMBER
             | NUMBER
             | NEGATIVENUMBER64
             | NUMBER64
             | HEX_STRING
             | BIN_STRING"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1]

  def p_enumSpec(self, p):
    """enumSpec : '{' enumItems '}'"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('enumSpec', p[2])
    # done

  def p_enumItems(self, p):
    """enumItems : enumItems ',' enumItem
                 | enumItem"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 4:
      p[0] = p[1] + [p[3]]
    elif n == 2:
      p[0] = [p[1]]
    # done

  def p_enumItem(self, p):
    """enumItem : LOWERCASE_IDENTIFIER '(' enumNumber ')'"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = (p[1], p[3])
    # done 

  def p_enumNumber(self, p):
    """enumNumber : NUMBER
                  | NEGATIVENUMBER"""
    # XXX              | LOWERCASE_IDENTIFIER"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1]
    # done

  def p_Status(self, p):
    """Status : LOWERCASE_IDENTIFIER"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    #  p[0] = ('Status', p[1]) 
    pass

  def p_Status_Capabilities(self, p):
    """Status_Capabilities : LOWERCASE_IDENTIFIER"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('Status_Capabilities', p[1])

  def p_DisplayPart(self, p):
    """DisplayPart : DISPLAY_HINT Text
                   | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      p[0] = (p[1], p[2])

  def p_UnitsPart(self, p):
    """UnitsPart : UNITS Text
                 | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      p[0] = (p[1], p[2])

  def p_Access(self, p):
    """Access : LOWERCASE_IDENTIFIER"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1]
    # done

  def p_IndexPart(self, p):
    """IndexPart : AUGMENTS '{' Entry '}'
                 | empty"""
    # XXX             |PIB_INDEX '{' Entry '}'
    # XXX             | EXTENDS '{' Entry '}'
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      p[0] = p[3]
    # done

  def p_MibIndex(self, p):
    """MibIndex : INDEX '{' IndexTypes '}'
                | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      p[0] = (p[1], p[3])
    # done

  def p_IndexTypes(self, p):
    """IndexTypes : IndexTypes ',' IndexType
                  | IndexType"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 4:
      p[0] = p[1] + [p[3]]
    elif n == 2:
      p[0] = [p[1]]
    # done

  def p_IndexType(self, p):
    """IndexType : IMPLIED Index
                 | Index"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 2:
      p[0] = (0, p[1])
    elif n == 3:
      p[0] = (1, p[2]) # IMPLIED
    # done

  def p_Index(self, p):
    """Index : ObjectName"""
    # libsmi: TODO: use the SYNTAX value of the correspondent 
    #               OBJECT-TYPE invocation
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1][1][0] # XXX just name???
    # done

  def p_Entry(self, p):
    """Entry : ObjectName"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] =  p[1][1][0]
    # done

  def p_DefValPart(self, p):
    """DefValPart : DEFVAL '{' Value '}'
                  | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1] and p[3]:
      p[0] = (p[1], p[3])
    # done

  def p_Value(self, p):
    """Value : valueofObjectSyntax
             | '{' BitsValue '}'"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 2:
      p[0] = p[1]
    elif n == 4:
      p[0] = p[2] 
    # done

  def p_BitsValue(self, p):
    """BitsValue : BitNames
                 | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      p[0] = p[1]
    # done

  def p_BitNames(self, p):
    """BitNames : BitNames ',' LOWERCASE_IDENTIFIER
                | LOWERCASE_IDENTIFIER"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 4:
      p[0] = ('BitNames', p[1][1] + [p[3]])
    elif n == 2:
      p[0] = ('BitNames', [p[1]])
    # done

  def p_ObjectName(self, p):
    """ObjectName : objectIdentifier"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1]
    # done

  def p_NotificationName(self, p):
    """NotificationName : objectIdentifier"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1]
    # done

  def p_ReferPart(self, p):
    """ReferPart : REFERENCE Text
                 | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    #if p[1]:
    #  p[0] = (p[1], p[2])
    pass

  def p_RevisionPart(self, p):
    """RevisionPart : Revisions
                    | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      p[0] = p[1]
    # done

  def p_Revisions(self, p):
    """Revisions : Revisions Revision
                 | Revision"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 3:
      p[0] = ('Revisions', p[1][1] + [p[2]])
    elif n == 2:
      p[0] = ('Revisions', [p[1]])
    # done

  def p_Revision(self, p):
    """Revision : REVISION ExtUTCTime DESCRIPTION Text"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[2] # revision time
           #  (p[3], p[4]) # description
    # done

  def p_NotificationObjectsPart(self, p):
    """NotificationObjectsPart : OBJECTS '{' Objects '}'
                               | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1] and p[3] or []
    # done

  def p_ObjectGroupObjectsPart(self, p):
    """ObjectGroupObjectsPart : OBJECTS '{' Objects '}'"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[3]
    # done

  def p_Objects(self, p):
    """Objects : Objects ',' Object
               | Object"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 4:
      p[0] = ('Objects', p[1][1] + [p[3]])
    elif n == 2:
      p[0] = ('Objects', [p[1]])
    # done

  def p_Object(self, p):
    """Object : ObjectName"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1][1][0]
    # done

  def p_NotificationsPart(self, p):
    """NotificationsPart : NOTIFICATIONS '{' Notifications '}'"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[3]
    # done

  def p_Notifications(self, p):
    """Notifications : Notifications ',' Notification
                     | Notification"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 4:
      p[0] = ('Notifications', p[1][1] + [p[3]])
    elif n == 2:
      p[0] = ('Notifications', [p[1]])
    # done 

  def p_Notification(self, p):
    """Notification : NotificationName"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1][1][0]
    # done

  def p_Text(self, p):
    """Text : QUOTED_STRING"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1][1:-1] # getting rid of quotes

  def p_ExtUTCTime(self, p):
    """ExtUTCTime : QUOTED_STRING"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    # p[0] = ('ExtUTCTime', p[1])
    p[0] = p[1][1:-1] # getting rid of quotes
    # done

  def p_objectIdentifier(self, p):
    """objectIdentifier : subidentifiers"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('objectIdentifier', p[1])
    # done

  def p_subidentifiers(self, p):
    """subidentifiers : subidentifiers subidentifier
                      | subidentifier"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 3:
      p[0] = p[1] + [p[2]]
    elif n == 2:
      p[0] = [p[1]]
    # done

  def p_subidentifier(self, p):
    """subidentifier : fuzzy_lowercase_identifier
                     | NUMBER
                     | LOWERCASE_IDENTIFIER '(' NUMBER ')'"""
    # also possible syntax according to libsmi
    # | moduleName '.' LOWERCASE_IDENTIFIER
    # | moduleName '.' LOWERCASE_IDENTIFIER '(' NUMBER ')'
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 2:
      p[0] = p[1]
    elif n == 5:
      p[0] = (p[1],p[3]) # XXX Do we need to create a new symbol p[1]?
    # done

  def p_objectIdentifier_defval(self, p):
    """objectIdentifier_defval : subidentifiers_defval"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('objectIdentifier_defval', p[1])

  def p_subidentifiers_defval(self, p):
    """subidentifiers_defval : subidentifiers_defval subidentifier_defval
                             | subidentifier_defval"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 3:
      p[0] = ('subidentifiers_defval', p[1][1] + [p[2]])
    elif n == 2:
      p[0] = ('subidentifiers_defval', [p[1]])

  def p_subidentifier_defval(self, p):
    """subidentifier_defval : LOWERCASE_IDENTIFIER '(' NUMBER ')'
                            | NUMBER"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 2:
      p[0] = ('subidentifier_defval', p[1])
    elif n == 5:
      p[0] = ('subidentifier_defval', p[1], p[3])

  def p_objectGroupClause(self, p):
    """objectGroupClause : LOWERCASE_IDENTIFIER OBJECT_GROUP ObjectGroupObjectsPart STATUS Status DESCRIPTION Text ReferPart COLON_COLON_EQUAL '{' objectIdentifier '}'"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('objectGroupClause', p[1], # id
                                 p[3], # objects
                               #  p[5], # status
                                 (p[6], p[7]), # description
                               #  p[8], # reference
                                 p[11]) # objectIdentifier

  def p_notificationGroupClause(self, p):
    """notificationGroupClause : LOWERCASE_IDENTIFIER NOTIFICATION_GROUP NotificationsPart STATUS Status DESCRIPTION Text ReferPart COLON_COLON_EQUAL '{' objectIdentifier '}'"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('notificationGroupClause', p[1], # id
                                       p[3], # notifications
                                     #  p[5], # status
                                       (p[6], p[7]), # description
                                     #  p[8], # reference
                                       p[11]) # objectIdentifier

  def p_moduleComplianceClause(self, p):
    """moduleComplianceClause : LOWERCASE_IDENTIFIER MODULE_COMPLIANCE STATUS Status DESCRIPTION Text ReferPart ComplianceModulePart COLON_COLON_EQUAL '{' objectIdentifier '}'"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('moduleComplianceClause', p[1], # id
                                    #  p[2], # MODULE_COMPLIANCE
                                    #  p[4], # status
                                      (p[5], p[6]), # description
                                    #  p[7], # reference
                                      p[8], # ComplianceModules
                                      p[11]) # objectIdentifier

  def p_ComplianceModulePart(self, p):
    """ComplianceModulePart : ComplianceModules"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1]
    # done

  def p_ComplianceModules(self, p):
    """ComplianceModules : ComplianceModules ComplianceModule
                         | ComplianceModule"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 3:
      p[0] = ('ComplianceModules', p[1][1] + [p[2]])
    elif n == 2:
      p[0] = ('ComplianceModules', [p[1]])
    # done

  def p_ComplianceModule(self, p):
    """ComplianceModule : MODULE ComplianceModuleName MandatoryPart CompliancePart"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    objects = p[3] and p[3][1] or []
    objects += p[4] and p[4][1] or []
    p[0] = (p[2], # ModuleName
            objects) # MandatoryPart + CompliancePart
    # done

  def p_ComplianceModuleName(self, p):
    """ComplianceModuleName : UPPERCASE_IDENTIFIER
                            | empty"""
    # XXX                   | UPPERCASE_IDENTIFIER objectIdentifier 
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1]
    # done

  def p_MandatoryPart(self, p):
    """MandatoryPart : MANDATORY_GROUPS '{' MandatoryGroups '}'
                     | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      p[0] = p[3]
    # done

  def p_MandatoryGroups(self, p):
    """MandatoryGroups : MandatoryGroups ',' MandatoryGroup
                       | MandatoryGroup"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 4:
      p[0] = ('MandatoryGroups', p[1][1] + [p[3]])
    elif n == 2:
      p[0] = ('MandatoryGroups', [p[1]])
    # done

  def p_MandatoryGroup(self, p):
    """MandatoryGroup : objectIdentifier"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[1][1][0] # objectIdentifier? Maybe name?
    # done

  def p_CompliancePart(self, p):
    """CompliancePart : Compliances
                      | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      p[0] = p[1]
    # done

  def p_Compliances(self, p):
    """Compliances : Compliances Compliance
                   | Compliance"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 3:
      p[0] = p[1] and p[2] and ('Compliances', p[1][1] + [p[2]]) or p[1]
    elif n == 2:
      p[0] = p[1] and ('Compliances', [p[1]]) or None
    # done

  def p_Compliance(self, p):
    """Compliance : ComplianceGroup
                  | ComplianceObject"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      p[0] = p[1]
    # done

  def p_ComplianceGroup(self, p):
    """ComplianceGroup : GROUP objectIdentifier DESCRIPTION Text"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = p[2][1][0] # objectIdentifier? Maybe name?
    #        p[1], # GROUP
    #        (p[3], p[4])) # description
    # done

  def p_ComplianceObject(self, p):
    """ComplianceObject : OBJECT ObjectName SyntaxPart WriteSyntaxPart AccessPart DESCRIPTION Text"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    #p[0] = (p[1], # object
    #        p[2], # name
    #        p[3], # syntax
    #        p[4], # write syntax
    #        p[5], # access
    #        (p[6], p[7])) # description
    pass

  def p_SyntaxPart(self, p):
    """SyntaxPart : SYNTAX Syntax
                  | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      p[0] = p[2]

  def p_WriteSyntaxPart(self, p):
    """WriteSyntaxPart : WRITE_SYNTAX WriteSyntax
                       | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      p[0] = p[2]

  def p_WriteSyntax(self, p):
    """WriteSyntax : Syntax"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('WriteSyntax', p[1])

  def p_AccessPart(self, p):
    """AccessPart : MIN_ACCESS Access
                  | PIB_MIN_ACCESS Access
                  | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      p[0] = (p[1], p[2])

  def p_agentCapabilitiesClause(self, p):
    """agentCapabilitiesClause : LOWERCASE_IDENTIFIER AGENT_CAPABILITIES PRODUCT_RELEASE Text STATUS Status_Capabilities DESCRIPTION Text ReferPart ModulePart_Capabilities COLON_COLON_EQUAL '{' objectIdentifier '}'"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('agentCapabilitiesClause', p[1], # id
                                    #   p[2], # AGENT_CAPABILITIES
                                    #   (p[3], p[4]), # product release
                                    #   p[6], # status capabilities
                                       (p[7], p[8]), # description
                                    #   p[9], # reference
                                    #   p[10], # module capabilities
                                       p[13]) # objectIdentifier
                                        
  def p_ModulePart_Capabilities(self, p):
    """ModulePart_Capabilities : Modules_Capabilities
                               | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    #if p[1]:
    #  p[0] = p[1]
    pass

  def p_Modules_Capabilities(self, p):
    """Modules_Capabilities : Modules_Capabilities Module_Capabilities
                            | Module_Capabilities"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    #n = len(p)
    #if n == 3:
    #  p[0] = ('Modules_Capabilities', p[1][1] + [p[2]])
    #elif n == 2:
    #  p[0] = ('Modules_Capabilities', [p[1]]) 
    pass

  def p_Module_Capabilities(self, p):
    """Module_Capabilities : SUPPORTS ModuleName_Capabilities INCLUDES '{' CapabilitiesGroups '}' VariationPart"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    #p[0] = ('Module_Capabilities', (p[1], p[2]), # supports
    #                               (p[3], p[5]), # includes
    #                               p[7]) # variations 
    pass

  def p_CapabilitiesGroups(self, p):
    """CapabilitiesGroups : CapabilitiesGroups ',' CapabilitiesGroup
                          | CapabilitiesGroup"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    #n = len(p)
    #if n == 4:
    #  p[0] = ('CapabilitiesGroups', p[1][1] + [p[3]])
    #elif n == 2:
    #  p[0] = ('CapabilitiesGroups', [p[1]])
    pass

  def p_CapabilitiesGroup(self, p):
    """CapabilitiesGroup : objectIdentifier"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    #p[0] = ('CapabilitiesGroup', p[1])
    pass

  def p_ModuleName_Capabilities(self, p):
    """ModuleName_Capabilities : UPPERCASE_IDENTIFIER objectIdentifier
                               | UPPERCASE_IDENTIFIER"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    #n = len(p)
    #if n == 2:
    #  p[0] = ('ModuleName_Capabilities', p[1])
    #elif n == 3:
    #  p[0] = ('ModuleName_Capabilities', p[1], p[2])
    pass

  def p_VariationPart(self, p):
    """VariationPart : Variations
                     | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    #if p[1]:
    #  p[0] = p[1]
    pass

  def p_Variations(self, p):
    """Variations : Variations Variation
                  | Variation"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    #n = len(p)
    #if n == 3:
    #  p[0] = ('Variations', p[1][1] + [p[2]])
    #elif n == 2:
    #  p[0] = ('Variations', [p[1]])
    pass

  def p_Variation(self, p):
    """Variation : VARIATION ObjectName SyntaxPart WriteSyntaxPart VariationAccessPart CreationPart DefValPart DESCRIPTION Text"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    #p[0] = (p[1], # variation
    #        p[2], # name
    #        p[3], # syntax
    #        p[4], # write syntax
    #        p[5], # access
    #        p[6], # creation
    #        p[7], # defval
    #        (p[8], p[9])) # description
    pass

  def p_VariationAccessPart(self, p):
    """VariationAccessPart : ACCESS VariationAccess
                           | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    #if p[1]:
    #  p[0] = (p[1], p[2])
    pass

  def p_VariationAccess(self, p):
    """VariationAccess : LOWERCASE_IDENTIFIER"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    #p[0] = p[1]
    pass

  def p_CreationPart(self, p):
    """CreationPart : CREATION_REQUIRES '{' Cells '}'
                    | empty"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    if p[1]:
      p[0] = (p[1], p[3])

  def p_Cells(self, p):
    """Cells : Cells ',' Cell
             | Cell"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    n = len(p)
    if n == 4:
      p[0] = ('Cells', p[1][1] + [p[3]])
    elif n == 2:
      p[0] = ('Cells', [p[1]])

  def p_Cell(self, p):
    """Cell : ObjectName"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    p[0] = ('Cell', p[1])

  def p_empty(self, p):
    """empty :"""
    #print inspect.currentframe().f_code.co_name, ': ', p[0:]
    pass

# Error rule for syntax errors
  def p_error(self, p):
    if p:
      raise error.PySmiError("Bad grammar near token type=%s, value=%s" % \
                             (p.type, p.value))
      # Just discard the token and tell the parser it's okay.
#    parser.errok()
#  else:
#    print 'p: '
    
#  f = 'RFC1065-SMI' # rare oid notation
#  f = 'UPS-MIB' # OBJECT_IDENTITY
#  f = 'VRRP-MIB' # augmentions
#  f = 'RFC1382-MIB' # TRAP_TYPE
#  f = 'WWW-MIB'
#  f = 'IPSEC-SPD-MIB'
#  f = 'SNMPv2-MIB'
#  f = 'MPLS-FTN-STD-MIB' # MODULE-COMPLIANCE with module name
