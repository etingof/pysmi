import sys
from time import strptime, strftime
from pysmi.codegen.base import AbstractCodeGen
from pysmi import error
from pysmi import debug

if sys.version_info[0] > 2:
    unicode = str
    long = int
    def dorepr(s): return repr(s)
else:
    def dorepr(s): return repr(s.encode('utf-8')).decode('utf-8')

# default pysnmp MIB packages
defaultMibPackages = ('pysnmp.smi.mibs', 'pysnmp_mibs')

# never compile these, they either:
# - define MACROs (implementation supplies them)
# - or carry conflicting OIDs (so that all IMPORT's of them will be rewritten)
# - or have manual fixes
# - or import base ASN.1 types from implementation-specific MIBs
baseMibs = ('RFC1065-SMI',
            'RFC1155-SMI',
            'RFC1158-MIB',
            'RFC-1212',
            'RFC-1213-MIB',
            'RFC-1215',
            'SNMPv2-SMI',
            'SNMPv2-TC',
            'SNMPv2-TM',
            'SNMPv2-CONF',
            'ASN1',
            'ASN1-ENUMERATION',
            'ASN1-REFINEMENT',
            'SNMP-FRAMEWORK-MIB',
            'SNMP-TARGET-MIB',
            'TRANSPORT-ADDRESS-MIB')

class PySnmpCodeGen(AbstractCodeGen):
  symsTable = {
    'MODULE-IDENTITY': ('ModuleIdentity',),
    'OBJECT-TYPE': ('MibScalar', 'MibTable', 'MibTableRow', 'MibTableColumn'),
    'NOTIFICATION-TYPE': ('NotificationType',),
    'TEXTUAL-CONVENTION': ('TextualConvention',),
    'MODULE-COMPLIANCE': ('ModuleCompliance',),
    'OBJECT-GROUP': ('ObjectGroup',),
    'NOTIFICATION-GROUP': ('NotificationGroup',),
    'AGENT-CAPABILITIES': ('AgentCapabilities',),
    'OBJECT-IDENTITY': ('ObjectIdentity',),
    'TRAP-TYPE': ('NotificationType',),  # smidump always uses NotificationType
    'NOTIFICATION-TYPE': ('NotificationType',)
  }

  constImports = {
    'ASN1': ('Integer', 'OctetString', 'ObjectIdentifier'),
    'ASN1-ENUMERATION': ('NamedValues',),
    'ASN1-REFINEMENT': ('ConstraintsUnion', 'ConstraintsIntersection', 'SingleValueConstraint', 'ValueRangeConstraint', 'ValueSizeConstraint'),
    'SNMPv2-SMI': ('iso',
                   'Bits', # XXX
                   'Integer32', # libsmi bug ??? 
                   'TimeTicks', # bug in some IETF MIB
                   'Counter32', # bug in some IETF MIB (e.g. DSA-MIB)
                   'Gauge32', # bug in some IETF MIB (e.g. DSA-MIB)
                   'MibIdentifier'), # OBJECT IDENTIFIER
  }

  convertImportv2 = {
    'RFC1155-SMI': { 'internet': ('SNMPv2-SMI', 'internet'),
                     'directory': ('SNMPv2-SMI', 'directory'),
                     'mgmt': ('SNMPv2-SMI', 'mgmt'),
                     'experimental': ('SNMPv2-SMI', 'experimental'),
                     'private': ('SNMPv2-SMI', 'private'),
                     'enterprises': ('SNMPv2-SMI', 'enterprises'),
                     'IpAddress': ('SNMPv2-SMI', 'IpAddress'),
                     'Counter': ('SNMPv2-SMI', 'Counter32'),
                     'Gauge': ('SNMPv2-SMI', 'Gauge32'),
                     'TimeTicks': ('SNMPv2-SMI', 'TimeTicks'),
                     'Opaque': ('SNMPv2-SMI', 'Opaque'),
                     'NetworkAddress': ('SNMPv2-SMI', 'IpAddress'),
                     'OBJECT-TYPE': ('SNMPv2-SMI', 'OBJECT-TYPE'),
    },
    'RFC1065-SMI': { 'internet': ('SNMPv2-SMI', 'internet'),
                     'directory': ('SNMPv2-SMI', 'directory'),
                     'mgmt': ('SNMPv2-SMI', 'mgmt'),
                     'experimental': ('SNMPv2-SMI', 'experimental'),
                     'private': ('SNMPv2-SMI', 'private'),
                     'enterprises': ('SNMPv2-SMI', 'enterprises'),
                     'IpAddress': ('SNMPv2-SMI', 'IpAddress'),
                     'Counter': ('SNMPv2-SMI', 'Counter32'),
                     'Gauge': ('SNMPv2-SMI', 'Gauge32'),
                     'TimeTicks': ('SNMPv2-SMI', 'TimeTicks'),
                     'Opaque': ('SNMPv2-SMI', 'Opaque'),
    },
    'RFC1213-MIB': { 'mib-2': ('SNMPv2-SMI', 'mib-2'),
                     'DisplayString': ('SNMPv2-TC', 'DisplayString'),
    },
    'RFC-1212': { 'OBJECT-TYPE': ('SNMPv2-SMI', 'OBJECT-TYPE'),
    },
    'RFC-1215': { 'TRAP-TYPE': ('SNMPv2-SMI', 'TRAP-TYPE'),
    },
  }

  typeClasses = {
    'COUNTER32': 'Counter32',
    'COUNTER64': 'Counter64',
    'GAUGE32': 'Gauge32',
    'INTEGER': 'Integer32', # XXX
    'INTEGER32': 'Integer32',
    'IPADDRESS': 'IpAddress',
    'OBJECT IDENTIFIER': 'ObjectIdentifier',
    'OCTET STRING': 'OctetString',
    'OPAQUE': 'Opaque',
    'TIMETICKS': 'TimeTicks',
    'UNSIGNED32': 'Unsigned32',
    'Counter': 'Counter32',
    'Gauge': 'Gauge32',
    'NetworkAddress': 'IpAddress',
  }

  ifTextStr = 'if mibBuilder.loadTexts: '
  indent = ' '*4

  def __init__(self):
    self._rows = set()
    self._cols = {} # k, v = name, datatype
    self._exports = set()
    self._presentedSyms = set()
    self._symsOrder = []
    self._postponedSyms = {} # k, v = name, (parent OID, generated code)
#    self._unknownDefvalType = {} # k, v = name, (defval, generated code w/stub)
    self._out = {} # k, v = name, generated code
    self.moduleName = ['DUMMY']
    self.genRules = { 'text' : 1 }
 
  def symTrans(self, symbol):
    if symbol in self.symsTable:
      return self.symsTable[symbol]
    return symbol,

  def transOpers(self, symbol):
    return symbol.replace('-', '_')

  def isBinary(self, s):
    return isinstance(s, (str, unicode)) and s[0] == '\'' \
                                         and s[-2:] in ('\'b', '\'B')

  def isHex(self, s):
    return isinstance(s, (str, unicode)) and s[0] == '\'' \
                                         and s[-2:] in ('\'h', '\'H')

  def str2int(self, s):
    if self.isBinary(s):
      if s[1:-2]:
        i = int(s[1:-2], 2)
      else:
        raise error.PySmiSemanticError('empty binary string to int conversion')
    elif self.isHex(s):
      if s[1:-2]:
        i = int(s[1:-2], 16)
      else:
        raise error.PySmiSemanticError('empty hex string to int conversion')
    else:
      i = int(s)
    return i
      
  def prepData(self, pdata, classmode = 0):
    data = []
    for el in pdata:
      if not isinstance(el, tuple):
        data.append(el)
      elif len(el) == 1:
          data.append(el[0])
      else:
        data.append(self.handlersTable[el[0]](self, self.prepData(el[1:], classmode=classmode), classmode=classmode)
        )
    return data 

  def genImports(self, imports):
    outStr = ''
    # convertion to SNMPv2
    toDel = []
    for module in list(imports):
      if module in self.convertImportv2:
        for symbol in imports[module]:
          if symbol in self.convertImportv2[module]:
            toDel.append((module, symbol))
            newModule, newSymbol = self.convertImportv2[module][symbol]
            if newModule in imports:
              imports[newModule].append(newSymbol)
            else:
              imports[newModule] = [newSymbol]
    # removing converted symbols
    for d in toDel:
      imports[d[0]].remove(d[1])
    # merging mib and constant imports
    for module in self.constImports:
      if module in imports:
        imports[module] += self.constImports[module]
      else:
        imports[module] = self.constImports[module]
    for module in sorted(imports):
      symbols = ()
      for symbol in set(imports[module]):
        symbols += self.symTrans(symbol)
      if symbols:
        self._presentedSyms = self._presentedSyms.union([self.transOpers(s) for s in symbols])
        outStr += '( %s, ) = mibBuilder.importSymbols("%s")\n' % \
          ( ', '.join([self.transOpers(s) for s in symbols]),
            '", "'.join((module,) + symbols) )
    return outStr, tuple(sorted(imports))

  def genExports(self, ):
    exports = list(self._exports)
    exportsNum = len(exports)
    chunkNum = exportsNum/254
    outStr = ''
    for i in range(int(chunkNum+1)):
      outStr += 'mibBuilder.exportSymbols("' + self.moduleName[0] + '", '
      outStr += ', '.join(exports[254*i:254*(i+1)]) + ')\n'
    return self._exports and outStr or ''

  def genLabel(self, symbol, classmode=0):
    if symbol.find('-') != -1:
      return classmode and 'label = "' + symbol + '"\n' or \
                           '.setLabel("' + symbol + '")'
    return ''

  def addToExports(self, symbol, moduleIdentity=0):
    if moduleIdentity:
      self._exports.add('PYSNMP_MODULE_ID=%s' % symbol)
    self._exports.add('%s=%s' % (symbol, symbol))
    self._presentedSyms.add(symbol)

  def regSym(self, symbol, outStr, parentOid=None, moduleIdentity=0):
    if symbol in self._presentedSyms or symbol in self._postponedSyms:
      raise error.PySmiSemanticError('Duplicate symbol found: %s' % symbol)
    if not parentOid or parentOid in self._presentedSyms:
      self._presentedSyms.add(symbol)
      self._symsOrder.append(symbol)
      self.regPostponedSyms()
    else: 
      self._postponedSyms[symbol] = (parentOid, outStr)
    self.addToExports(symbol, moduleIdentity)
    self._out[symbol] = outStr

  def regPostponedSyms(self):
    regedSyms = []
    for sym, val in self._postponedSyms.items():
      parent, code = val
      if parent in self._presentedSyms:
        self._presentedSyms.add(sym)
        self._symsOrder.append(sym)
        regedSyms.append(sym)
    for sym in regedSyms:
      self._postponedSyms.pop(sym)

### Clause generation functions
  def genAgentCapabilities(self, data, classmode=0):
    name, description, oid = data
    label = self.genLabel(name)
    name = self.transOpers(name)
    oidStr, parentOid = oid
    outStr =  name + ' = AgentCapabilities(' + oidStr + ')' + label + '\n'
    if self.genRules['text']:
      outStr += self.ifTextStr + name + description + '\n'
    self.regSym(name, outStr, parentOid)
    return outStr

  def genModuleIdentity(self, data, classmode=0):
    name, organization, contactInfo, description, revisions, oid  = data
    label = self.genLabel(name)
    name = self.transOpers(name)
    oidStr, parentOid = oid
    revisions = revisions and revisions or ''
    outStr = name + ' = ModuleIdentity(' + oidStr + ')' + label + revisions + '\n'
    if self.genRules['text']:
      outStr += self.ifTextStr + name + organization + '\n' 
      outStr += self.ifTextStr + name + contactInfo + '\n' 
      outStr += self.ifTextStr + name + description + '\n' 
    self.regSym(name, outStr, parentOid, moduleIdentity=1)
    return outStr

  def genModuleCompliance(self, data, classmode=0):
    name, description, compliances, oid = data
    label = self.genLabel(name)
    name = self.transOpers(name)
    oidStr, parentOid = oid
    outStr = name + ' = ModuleCompliance(' + oidStr + ')' + label
    outStr += compliances + '\n'
    if self.genRules['text']:
      outStr += self.ifTextStr + name + description + '\n'
    self.regSym(name, outStr, parentOid)
    return outStr

  def genNotificationGroup(self, data, classmode=0):
    name, objects, description, oid = data
    label = self.genLabel(name)
    name = self.transOpers(name)
    oidStr, parentOid = oid
    objStr = ''
    if objects:
      objects = [ '("' + self.moduleName[0] + '", "' + self.transOpers(obj) + '"),' \
                  for obj in objects ]
    objStr = ' '.join(objects)
    outStr = name + ' = NotificationGroup(' + oidStr + ')' + label
    outStr += '.setObjects(*(' + objStr + '))\n'
    if self.genRules['text']:
      outStr += self.ifTextStr + name + description + '\n'
    self.regSym(name, outStr, parentOid)
    return outStr  

  def genNotificationType(self, data, classmode=0):
    name, objects, description, oid = data
    label = self.genLabel(name)
    name = self.transOpers(name)
    oidStr, parentOid = oid
    objStr = ''
    if objects:
      objects = [ '("' + self.moduleName[0] + '", "' + self.transOpers(obj) + '"),' \
                  for obj in objects ]
    objStr = ' '.join(objects)
    outStr = name + ' = NotificationType(' + oidStr + ')' + label
    outStr += '.setObjects(*(' + objStr + '))\n'
    if self.genRules['text']:
      outStr += self.ifTextStr + name + description + '\n'
    self.regSym(name, outStr, parentOid)
    return outStr

  def genObjectGroup(self, data, classmode=0):
    name, objects, description, oid = data
    label = self.genLabel(name)
    name = self.transOpers(name)
    oidStr, parentOid = oid
    objStr = ''
    if objects:
      objects = [ '("' + self.moduleName[0] + '", "' + self.transOpers(obj) + '"),' \
                  for obj in objects ]
    objStr = ' '.join(objects)
    outStr = name + ' = ObjectGroup(' + oidStr + ')' + label
    outStr += '.setObjects(*(' + objStr + '))\n'
    if self.genRules['text']:
      outStr += self.ifTextStr + name + description + '\n'
    self.regSym(name, outStr, parentOid)
    return outStr

  def genObjectIdentity(self, data, classmode=0):
    name, description, oid = data
    label = self.genLabel(name)
    name = self.transOpers(name)
    oidStr, parentOid = oid
    outStr =  name + ' = ObjectIdentity(' + oidStr + ')' + label + '\n'
    if self.genRules['text']:
      outStr += self.ifTextStr + name + description + '\n'
    self.regSym(name, outStr, parentOid)
    return outStr

  def genObjectType(self, data, classmode=0):
    name, syntax, units, maxaccess, description, augmention, index, defval, oid = data
    label = self.genLabel(name)
    name = self.transOpers(name)
    oidStr, parentOid = oid
    subtype = syntax[0] == 'Bits' and 'Bits()' + syntax[1] or \
                                      syntax[1] # Bits hack #1
    classtype = self.typeClasses.get(syntax[0], syntax[0])
    classtype = syntax[0] == 'Bits' and 'MibScalar' or classtype # Bits hack #2
    classtype = name in self._cols and 'MibTableColumn' or classtype
    outStr = name + ' = ' + classtype  + '(' + oidStr  + ', ' + subtype + \
             (defval and defval or '') + ')' + label
    outStr += (units and units) or ''
    outStr += (maxaccess and maxaccess) or ''
    outStr += (index and index) or ''
    outStr += '\n'
    if augmention:
      augmention = self.transOpers(augmention)
      outStr += augmention + '.registerAugmentions(("' + self.moduleName[0] + \
                '", "' + name + '"))\n'
      outStr += name + '.setIndexNames(*' + augmention + '.getIndexNames())\n'
    if self.genRules['text'] and description:
      outStr += self.ifTextStr + name + description + '\n'
    self.regSym(name, outStr, parentOid)
    return outStr

  def genTrapType(self, data, classmode=0):
    name, enterprise, variables, description, value = data
    label = self.genLabel(name)
    name = self.transOpers(name)
    enterpriseStr, parentOid = enterprise
    varStr = ''
    if variables:
      variables = [ '("' + self.moduleName[0] + '", "' + self.transOpers(var) + '"),' \
                    for var in variables ]
    varStr = ' '.join(variables)   
    outStr = name + ' = NotificationType(' + enterpriseStr + \
             ' + (0,' + str(value) + '))' + label
    outStr += '.setObjects(*(' + varStr + '))\n'
    if self.genRules['text']:
      outStr += self.ifTextStr + name + description + '\n'
    self.regSym(name, outStr, parentOid)
    return outStr

  def genTypeDeclaration(self, data, classmode=0):
    outStr = ''
    name, declaration = data
    if declaration:
      parentType, attrs = declaration
      if parentType: # skipping SEQUENCE case
        name = self.transOpers(name)
        outStr = 'class ' + name + '(' + parentType +'):\n' + attrs + '\n'
        self.regSym(name, outStr)
    return outStr 

  def genValueDeclaration(self, data, classmode=0):
    name, oid = data
    label = self.genLabel(name)
    name = self.transOpers(name)
    oidStr, parentOid = oid
    outStr = name + ' = MibIdentifier(' + oidStr + ')' + label + '\n'
    self.regSym(name, outStr, parentOid)
    return outStr

### Subparts generation functions
  def genBitNames(self, data, classmode=0):
    names = data[0]
    return '("' + '","'.join(names) + '",)'  

  def genBits(self, data, classmode=0):
    bits = data[0]
    namedval = [ '("' + bit[0] + '", ' +  str(bit[1]) + '),' for bit in bits ] 
    numFuncCalls = len(namedval)/255 + 1
    funcCalls = ''
    for i in range(int(numFuncCalls)):
      funcCalls += 'NamedValues(' + ' '.join(namedval[255*i:255*(i+1)]) + ') + ' 
    funcCalls = funcCalls[:-3]
    outStr = classmode and \
      self.indent + 'namedValues = ' + funcCalls + '\n' or \
      '.clone(namedValues=' + funcCalls + ')'
    return 'Bits', outStr

  def genCompliances(self, data, classmode=0):
    complStr = ''
    compliances = []
    for complianceModule in data[0]:
      name = complianceModule[0] or self.moduleName[0]
      compliances += [ '("' + name + '", "' + self.transOpers(compl) + '"),' \
                       for compl in complianceModule[1] ]
    complStr = ' '.join(compliances)
    return '.setObjects(*(' + complStr + '))'

  def genConceptualTable(self, data, classmode=0):
    row = data[0]
    if row[1] and row[1][-2:] == '()':
      row = row[1][:-2]
      self._rows.add(row)
    return 'MibTable', ''

  def genContactInfo(self, data, classmode=0):
    text = data[0]
    return '.setContactInfo(' + dorepr(text) + ')'

  def genDisplayHint(self, data, classmode=0):
    return self.indent + 'displayHint = ' + dorepr(data[0]) + '\n'
   
  def genDefVal(self, data, classmode=0):
    defval = data[0]
    if isinstance(defval, (int, long)): # number
      val = str(defval)
    elif self.isHex(defval): # hex
      val = 'hexValue="' + defval[1:-2] + '"'
    elif self.isBinary(defval): # binary
      binval = defval[1:-2]
      hexval = binval and hex(int(binval, 2))[2:] or ''
      val = 'hexValue="' + hexval + '"'
    elif defval[0] == defval[-1] and defval[0] == '(': # bits list
      val = defval
    elif defval[0] == defval[-1] and defval[0] == '"': # quoted strimg
      val = dorepr(defval[1:-1])
    else: # symbol (oid as defval) or name for enumeration member
      if defval in self._presentedSyms:
        val = defval + '.getName()' 
      else:
        val = dorepr(defval)
    return '.clone(' + val + ')'

  def genDescription(self, data, classmode=0):
    text = data[0]
    return '.setDescription(' + dorepr(text) + ')'

  def genEnumSpec(self, data, classmode=0):
    items = data[0]
    singleval = [ str(item[1]) + ',' for item in items ]
    outStr = classmode and self.indent + 'subtypeSpec = %s.subtypeSpec+' or \
             '.subtype(subtypeSpec='
    numFuncCalls = len(singleval)/255 + 1
    singleCall = numFuncCalls == 1 or False
    funcCalls = ''
    outStr += not singleCall and 'ConstraintsUnion(' or ''
    for i in range(int(numFuncCalls)):
      funcCalls += 'SingleValueConstraint(' + \
                        ' '.join(singleval[255*i:255*(i+1)]) + '), '
    funcCalls = funcCalls[:-2]
    outStr += funcCalls
    outStr += not singleCall and \
              (classmode and ')\n' or '))') or \
              (not classmode and ')' or '\n')  
    outStr += self.genBits(data, classmode=classmode)[1]
    return outStr

  def genIndex(self, data, classmode=0):
    indexes = data[0]
    indexes = ['(' + str(ind[0]) + ', "' + self.moduleName[0] + '", "' + ind[1] + '")' \
               for ind in indexes ]
    return '.setIndexNames(' + ', '.join(indexes)+ ')'

  def genIntegerSubType(self, data, classmode=0):
    singleRange = len(data[0]) == 1 or False
    outStr = classmode and self.indent + 'subtypeSpec = %s.subtypeSpec+' or \
                           '.subtype(subtypeSpec='
    outStr += not singleRange and 'ConstraintsUnion(' or ''
    for range in data[0]:
      vmin, vmax = len(range) == 1 and (range[0], range[0]) or range
      vmin, vmax = str(self.str2int(vmin)), str(self.str2int(vmax))
      outStr += 'ValueRangeConstraint(' + vmin + ',' + vmax + ')' + \
                (not singleRange and ',' or '')
    outStr += not singleRange and \
              (classmode and ')' or '))') or \
              (not classmode and ')' or '\n')
    return outStr

  def genMaxAccess(self, data, classmode=0):
    access = data[0].replace('-', '')
    return access != 'notaccessible' and '.setMaxAccess("' + access + '")' or ''

  def genOctetStringSubType(self, data, classmode=0):
    singleRange = len(data[0]) == 1 or False
    outStr = classmode and self.indent + 'subtypeSpec = %s.subtypeSpec+' or \
                           '.subtype(subtypeSpec='
    outStr += not singleRange and 'ConstraintsUnion(' or ''
    for range in data[0]:
      vmin, vmax = len(range) == 1 and (range[0], range[0]) or range
      vmin, vmax = str(self.str2int(vmin)), str(self.str2int(vmax))
      outStr += 'ValueSizeConstraint(' + vmin + ',' + vmax + ')' + \
                (not singleRange and ',' or '')
    outStr += not singleRange and \
              (classmode and ')' or '))') or \
              (not classmode and ')' or '\n') 
    outStr += singleRange and vmin==vmax and \
              (classmode and self.indent + 'fixedLength = ' + vmin + '\n' or \
                             '.setFixedLength(' + vmin + ')'
              ) or ''
    return outStr

  def genOid(self, data, classmode=0):
    outStr = ''
    parent = '' 
    for el in data[0]:
      if isinstance(el, (str, unicode)):
        parent = self.transOpers(el)
        s = parent + '.getName()'
      elif isinstance(el, int):
        s = '(' + str(el) + ',)'
      elif isinstance(el, tuple):
        s = '(' + str(el[1]) + ',)' # XXX Do we need to create a new object el[0]?
      else:
        raise error.PySmiSemanticError('unknown datatype for OID')
      outStr += not outStr and s or ' + ' + s 
    return outStr, parent

  def genObjects(self, data, classmode=0):
    if data[0]:
      return [ self.transOpers(obj) for obj in data[0] ] # XXX self.transOpers or not??
    return []

  def genTime(self, data, classmode=0):
    times = []
    for t in data:
      lenTimeStr = len(t)
      if lenTimeStr == 11:
        t = '19' + t
      elif lenTimeStr != 13:
        raise error.PySmiSemanticError("Invalid date %s" % t)
      try:
        times.append(strftime('%Y-%m-%d %H:%M', strptime(t, '%Y%m%d%H%MZ')))
      except ValueError:
        raise error.PySmiSemanticError("Invalid date %s: %s" % (t, sys.exc_info()[1]))

    return times

  def genOrganization(self, data, classmode=0):
    text = data[0]
    return '.setOrganization(' + dorepr(text) + ')'

  def genRevisions(self, data, classmode=0):
    times = self.genTime(data[0]) 
    return '.setRevisions(("' + '", "'.join(times) + '",))'

  def genRow(self, data, classmode=0):
    row = data[0]
    return row in self._rows and ('MibTableRow', '') or self.genSimpleSyntax(data, classmode=classmode)

  def genSequence(self, data, classmode=0):
    cols = data[0]
    self._cols.update(cols)
    return '', ''

  def genSimpleSyntax(self, data, classmode=0):
    objType = data[0]
    objType = self.typeClasses.get(objType, objType)
    subtype = len(data) == 2 and data[1] or ''
    if classmode:
      subtype = '%s' in subtype and subtype % objType or subtype # XXX hack?
      return objType, subtype
    outStr = objType + '()' + subtype
    return 'MibScalar', outStr

  def genTypeDeclarationRHS(self, data, classmode=0):
    if len(data) == 1:
      parentType, attrs = data[0] # just syntax
    else:
      # Textual convention
      display, syntax = data
      parentType, attrs = syntax
      parentType = 'TextualConvention, ' + parentType
      attrs = (display and display or '') + attrs
    attrs = attrs or self.indent + 'pass\n'
    return parentType, attrs

  def genUnits(self, data, classmode=0):
    text = data[0]
    return '.setUnits(' + dorepr(text) + ')'

  handlersTable = {
    'agentCapabilitiesClause': genAgentCapabilities,
    'moduleIdentityClause': genModuleIdentity,
    'moduleComplianceClause': genModuleCompliance,
    'notificationGroupClause': genNotificationGroup,
    'notificationTypeClause': genNotificationType,
    'objectGroupClause': genObjectGroup,
    'objectIdentityClause': genObjectIdentity,
    'objectTypeClause': genObjectType,
    'trapTypeClause': genTrapType,
    'typeDeclaration': genTypeDeclaration,
    'valueDeclaration': genValueDeclaration,

    'ApplicationSyntax': genSimpleSyntax,
    'BitNames': genBitNames,
    'BITS': genBits,
    'ComplianceModules': genCompliances,
    'conceptualTable': genConceptualTable,
    'CONTACT-INFO': genContactInfo,
    'DISPLAY-HINT': genDisplayHint,
    'DEFVAL': genDefVal,
    'DESCRIPTION': genDescription,
    'enumSpec': genEnumSpec,
    'INDEX': genIndex,
    'integerSubType': genIntegerSubType,
    'MaxAccessPart': genMaxAccess,
    'Notifications': genObjects,
    'octetStringSubType': genOctetStringSubType,
    'objectIdentifier': genOid,
    'Objects': genObjects,
    'ORGANIZATION': genOrganization,
    'Revisions' : genRevisions,
    'row': genRow,
    'SEQUENCE': genSequence,
    'SimpleSyntax': genSimpleSyntax,
    'typeDeclarationRHS': genTypeDeclarationRHS,
    'UNITS': genUnits,
    'VarTypes': genObjects,
    #'a': lambda x: genXXX(x, 'CONSTRAINT')
  }

  def genCode(self, ast, genTexts=False):
    out =  ''
    importedModules = ()
    self.genRules['text'] = genTexts
    if ast and ast[0] == 'mibFile' and ast[1]: # mibfile is not empty
      modules = ast[1]
      for moduleid in range(len(modules)):
        self.moduleName[0], moduleOid, imports, declarations = modules[moduleid]
        self._rows.clear()
        self._cols.clear()
        self._exports.clear()
        self._presentedSyms.clear()
        self._symsOrder = []
        self._postponedSyms.clear()
#        self._unknownDefvalType.clear()
        self._out.clear()
        out, importedModules = self.genImports(imports and imports or {})
        for declr in declarations and declarations or []:
          if declr:
            clausetype = declr[0]
            classmode = clausetype == 'typeDeclaration'
            self.handlersTable[declr[0]](self, self.prepData(declr[1:], classmode), classmode)
        if self._postponedSyms:
          raise error.PySmiSemanticError('Unknown parent OIDs for symbols: %s' % ', '.join(self._postponedSyms)) 
        for sym in self._symsOrder:
          if sym not in self._out:
            raise error.PySmiCodegenError('No generated code for symbol %s' % sym)
          out += self._out[sym] 
        out += self.genExports()
    debug.logger & debug.flagCodegen and debug.logger('canonical MIB name %s, imported MIB(s) %s, Python code size %s bytes' % (self.moduleName[0], ','.join(importedModules) or '<none>', len(out)))
    return self.moduleName[0], importedModules, out

