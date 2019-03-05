#
# This file is part of pysmi software.
#
# Copyright (c) 2015-2019, Ilya Etingof <etingof@gmail.com>
# License: http://snmplabs.com/pysmi/license.html
#
import sys
import os
try:
    import json
except ImportError:
    import simplejson as json
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


class JsonCodeGen(IntermediateCodeGen):
    """Turns MIB AST into JSON document.

    Builds JSON document representing MIB module supplied in form of
    an Abstract Syntax Tree on input.

    Instance of this class is supposed to be passed to *MibCompiler*,
    the rest is internal to *MibCompiler*.
    """
    TEMPLATE_NAME = 'jsondoc/base.j2'

    def genCode(self, ast, symbolTable, **kwargs):
        mibInfo, context = IntermediateCodeGen.genCode(self, ast, symbolTable, **kwargs)

        # TODO: reduce code duplication with the other codegens

        searchPath = os.path.join(os.path.dirname(__file__), 'templates')

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
            '%s, JSON document size %d bytes' % (
                mibInfo.name, mibInfo.identity,
                ','.join(mibInfo.imported) or '<none>',
                dstTemplate, len(text)))

        return mibInfo, text

    # TODO: move this to a template
    def genIndex(self, processed, **kwargs):
        outDict = {
            'meta': {},
            'identity': {},
            'enterprise': {},
            'compliance': {},
            'oids': {},
        }
        if kwargs.get('old_index_data'):
            try:
                outDict.update(
                    json.loads(kwargs['old_index_data'])
                )

            except Exception:
                raise error.PySmiCodegenError('Index load error: %s' % sys.exc_info()[1])

        def order(top):
            if isinstance(top, dict):
                new_top = OrderedDict()
                try:
                    # first try to sort keys as OIDs
                    for k in sorted(top, key=lambda x: [int(y) for y in x.split('.')]):
                        new_top[k] = order(top[k])

                except ValueError:
                    for k in sorted(top):
                        new_top[k] = order(top[k])

                return new_top
            elif isinstance(top, list):
                new_top = []
                for e in sorted(set(top)):
                    new_top.append(order(e))

                return new_top

            return top

        for module, status in processed.items():
            modData = outDict['identity']
            identity_oid = getattr(status, 'identity', None)
            if identity_oid:
                if identity_oid not in modData:
                    modData[identity_oid] = []

                modData[identity_oid].append(module)

            modData = outDict['enterprise']
            enterprise_oid = getattr(status, 'enterprise', None)
            if enterprise_oid:
                if enterprise_oid not in modData:
                    modData[enterprise_oid] = []

                modData[enterprise_oid].append(module)

            modData = outDict['compliance']
            compliance_oids = getattr(status, 'compliance', ())
            for compliance_oid in compliance_oids:
                if compliance_oid not in modData:
                    modData[compliance_oid] = []
                modData[compliance_oid].append(module)

            modData = outDict['oids']
            objects_oids = getattr(status, 'oids', ())
            for object_oid in objects_oids:
                if object_oid not in modData:
                    modData[object_oid] = []

                modData[object_oid].append(module)

            if modData:
                unique_prefixes = {}
                for oid in sorted(modData, key=lambda x: x.count('.')):
                    for oid_prefix, modules in unique_prefixes.items():
                        if oid.startswith(oid_prefix) and set(modules).issuperset(modData[oid]):
                            break
                    else:
                        unique_prefixes[oid] = modData[oid]

                outDict['oids'] = unique_prefixes

        if 'comments' in kwargs:
            outDict['meta']['comments'] = kwargs['comments']

        debug.logger & debug.flagCodegen and debug.logger(
            'OID->MIB index built, %s entries' % len(processed))

        return json.dumps(order(outDict), indent=2)
