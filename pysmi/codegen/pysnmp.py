#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2020, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysmi/license.html
#
import sys
import os
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from pysmi.codegen.intermediate import IntermediateCodeGen
from pysmi.codegen import jfilters
from pysmi import error
from pysmi import debug

import jinja2


if sys.version_info[0] > 2:
    # noinspection PyShadowingBuiltins
    unicode = str
    # noinspection PyShadowingBuiltins
    long = int


class PySnmpCodeGen(IntermediateCodeGen):
    """Turns MIB AST into pysnmp Python code.

    Builds Python module representing MIB module in terms of pysnmp objects
    from MIB supplied in form of an Abstract Syntax Tree on input.

    Instance of this class is supposed to be passed to *MibCompiler*,
    the rest is internal to *MibCompiler*.
    """

    defaultMibPackages = ('pysnmp.smi.mibs', 'pysnmp_mibs')

    TEMPLATE_NAME = 'pysnmp/mib-definitions.j2'

    SMI_OBJECTS = {
        'MODULE-IDENTITY': ['ModuleIdentity'],
        'OBJECT-TYPE': ['MibScalar', 'MibTable', 'MibTableRow', 'MibTableColumn'],
        'NOTIFICATION-TYPE': ['NotificationType'],
        'TEXTUAL-CONVENTION': ['TextualConvention'],
        'MODULE-COMPLIANCE': ['ModuleCompliance'],
        'OBJECT-GROUP': ['ObjectGroup'],
        'NOTIFICATION-GROUP': ['NotificationGroup'],
        'AGENT-CAPABILITIES': ['AgentCapabilities'],
        'OBJECT-IDENTITY': ['ObjectIdentity'],
        'TRAP-TYPE': ['NotificationType'],
        'BITS': ['Bits']
    }

    SMI_TYPES = {
        'COUNTER32': 'Counter32',
        'COUNTER64': 'Counter64',
        'GAUGE32': 'Gauge32',
        'INTEGER': 'Integer32',  # XXX
        'INTEGER32': 'Integer32',
        'IPADDRESS': 'IpAddress',
        'NETWORKADDRESS': 'IpAddress',
        'OBJECT IDENTIFIER': 'ObjectIdentifier',
        'OCTET STRING': 'OctetString',
        'OPAQUE': 'Opaque',
        'TIMETICKS': 'TimeTicks',
        'UNSIGNED32': 'Unsigned32',
        'Counter': 'Counter32',
        'Gauge': 'Gauge32',
        'NetworkAddress': 'IpAddress',  # RFC1065-SMI, RFC1155-SMI -> SNMPv2-SMI
        'nullSpecific': 'zeroDotZero',  # RFC1158-MIB -> SNMPv2-SMI
        'ipRoutingTable': 'ipRouteTable',  # RFC1158-MIB -> RFC1213-MIB
        'snmpEnableAuthTraps': 'snmpEnableAuthenTraps'  # RFC1158-MIB -> SNMPv2-MIB
    }

    # never compile these, they either:
    # - define MACROs (implementation supplies them)
    # - or carry conflicting OIDs (so that all IMPORT's of them will be rewritten)
    # - or have manual fixes
    # - or import base ASN.1 types from implementation-specific MIBs
    fakeMibs = ('ASN1',
                'ASN1-ENUMERATION',
                'ASN1-REFINEMENT')
    baseMibs = ('PYSNMP-USM-MIB',
                'SNMP-FRAMEWORK-MIB',
                'SNMP-TARGET-MIB',
                'TRANSPORT-ADDRESS-MIB',
                'INET-ADDRESS-MIB') + IntermediateCodeGen.baseMibs

    def genCode(self, ast, symbolTable, **kwargs):
        mibInfo, context = IntermediateCodeGen.genCode(self, ast, symbolTable, **kwargs)

        # Adapt intermediate context to pysnmp template requirements

        # Translate SMI objects names in IMPORT

        imports = OrderedDict()

        for module, symbols in context.get('imports', {}).items():
            if not isinstance(symbols, list):
                continue

            imports[module] = []

            for symbol in symbols:
                if symbol in self.SMI_OBJECTS:
                    imports[module].extend(self.SMI_OBJECTS[symbol])
                else:
                    imports[module].append(symbol)

        context['imports'] = imports

        # Turn string OIDs into tuples which is native to pysnmp
        # TODO: we should make intermediate format producing tuples

        def translateOids(dct):
            for key, value in tuple(dct.items()):
                if isinstance(value, dict):
                    translateOids(value)
                elif key == 'oid':
                    dct[key] = tuple(int(x) for x in value.split('.'))

        translateOids(context)

        # Translate SMI types into pysnmp class names

        # Sort Managed Objects by OID
        objects = OrderedDict()

        for symbol, definition in sorted(
                context.items(), key=lambda x: x[1].get('oid', ())):
            objects[symbol] = definition

        context = objects

        # Render Python code

        searchPath = [os.path.join(os.path.dirname(__file__), 'templates')]

        # TODO: add unit test on custom template

        dstTemplate = kwargs.get('dstTemplate')
        if dstTemplate:
            searchPath.insert(0, os.path.dirname(os.path.abspath(dstTemplate)))

        env = jinja2.Environment(loader=jinja2.FileSystemLoader(searchPath),
                                 trim_blocks=True, lstrip_blocks=True)

        env.filters['capfirst'] = jfilters.capfirst

        try:
            tmpl = env.get_template(dstTemplate or self.TEMPLATE_NAME)
            text = tmpl.render(mib=context)

        except jinja2.exceptions.TemplateError:
            err = sys.exc_info()[1]
            raise error.PySmiCodegenError('Jinja template rendering error: %s' % err)

        debug.logger & debug.flagCodegen and debug.logger(
            'canonical MIB name %s (%s), imported MIB(s) %s, rendered from '
            '%s, Python code size %d bytes' % (
                mibInfo.name, mibInfo.identity,
                ','.join(mibInfo.imported) or '<none>',
                dstTemplate, len(text)))

        return mibInfo, text


# backward compatibility
baseMibs = PySnmpCodeGen.baseMibs
fakeMibs = PySnmpCodeGen.fakeMibs
