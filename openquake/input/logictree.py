# -*- coding: utf-8 -*-

# Copyright (c) 2010-2011, GEM Foundation.
#
# OpenQuake is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# only, as published by the Free Software Foundation.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License version 3 for more details
# (a copy is included in the LICENSE file that accompanied this code).
#
# You should have received a copy of the GNU Lesser General Public License
# version 3 along with OpenQuake.  If not, see
# <http://www.gnu.org/licenses/lgpl-3.0.txt> for a copy of the LGPLv3 License.

"""Logic tree parser, verifier and processor."""

import os
import sys
import re
from decimal import Decimal

from lxml import etree


class LogicTreeError(Exception):
    pass

class ParsingError(LogicTreeError):
    def __init__(self, filename, msg):
        super(ParsingError, self).__init__(msg)
        self.filename = filename

    def __str__(self):
        return 'file %s: %s' % (self.filename, self.message)

class ValidationError(LogicTreeError):
    def __init__(self, node, msg):
        super(ValidationError, self).__init__(msg)
        self.lineno = node.sourceline
        self.filename = node.getroottree().docinfo.URL

    def __str__(self):
        return 'file %s line %s: %s' % (self.filename, self.lineno,
                                        self.message)


class Branch(object):
    def __init__(self, branch_id, weight, value):
        self.branch_id = branch_id
        self.weight = weight
        self.value = value
        self.child_branchset = None

    def __str__(self):
        ret = '%s: %s' % (self.weight, self.value)
        if self.child_branchset:
            ret = '%s\n%s' % (ret, self.child_branchset)
        return ret


class BranchSet(object):
    def __init__(self, branches, uncertainty_type, filters):
        self.branches = branches
        self.uncertainty_type = uncertainty_type
        self.filters = filters

    def __str__(self):
        if self.filters:
            filters = ' %s' % ' '.join('%s="%s"' % item
                                       for item in self.filters.items())
        else:
            filters = ''
        ret = ['%s%s:' % (self.uncertainty_type, filters)]
        for branch in self.branches:
            lines = iter(str(branch).split('\n'))
            ret.append('  - %s' % next(lines))
            ret.extend('    %s' % line for line in lines)
        return '\n'.join(ret)


class LogicTree(object):
    SCHEMA_PATH = os.path.join(os.path.dirname(__file__),
                               '..', 'nrml', 'schema', 'nrml.xsd')
    NRML = 'http://openquake.org/xmlns/nrml/0.2'

    SOURCE_TYPES = ('pointSource', 'areaSource', 'complexFault', 'simpleFault')

    FILTERS = ('applyToTectonicRegionType',
               'applyToSource',
               'applyToSources',
               'applyToSourceType')

    _xmlschema = None

    @classmethod
    def get_xmlschema(cls):
        if not cls._xmlschema:
            cls._xmlschema = etree.XMLSchema(file=cls.SCHEMA_PATH)
        return cls._xmlschema

    def __init__(self, base_path, filename):
        self.base_path = base_path
        filepath = os.path.join(base_path, filename)
        parser = etree.XMLParser(schema=self.get_xmlschema())
        try:
            tree = etree.parse(filepath, parser=parser)
        except etree.XMLSyntaxError as exc:
            raise ParsingError(filepath, str(exc))
        [tree] = tree.getroot()
        self.branches = {}
        self.open_ends = set()
        self.source_ids = {}
        self.source_types = {}
        self.tectonic_region_types = {}
        self.parse_tree(tree)

    def parse_tree(self, tree):
        branchinglevels = iter(tree)
        [root_branchset] = next(branchinglevels)
        self.root = self.parse_branchset(root_branchset)
        if self.root.uncertainty_type != 'sourceModel':
            raise ValidationError(
                root_branchset,
                'first branchset must define an uncertainty ' \
                'of type "sourceModel"'
            )
        for source_model_branch in self.root.branches:
            self.collect_source_model_data(source_model_branch.value)
        for branchinglevel in branchinglevels:
            for branchset_node in branchinglevel:
                branchset = self.parse_branchset(branchset_node)
                if branchset.uncertainty_type == 'sourceModel':
                    raise ValidationError(
                        branchset_node,
                        'uncertainty of type "sourceModel" can be defined ' \
                        'on first branchset only'
                    )

    def parse_branchset(self, branchset_node):
        branches = []
        weight_sum = 0
        uncertainty_type = branchset_node.get('uncertaintyType')
        for branchnode in branchset_node:
            weight = branchnode.find('{%s}uncertaintyWeight' % self.NRML).text
            weight = Decimal(weight)
            weight_sum += weight
            value_node = branchnode.find('{%s}uncertaintyModel' % self.NRML)
            value = self.validate_uncertainty_value(
                value_node, uncertainty_type, value_node.text
            )
            branch_id = branchnode.get('branchID')
            branch = Branch(branch_id, weight, value)
            self.branches[branch_id] = branch
            branches.append(branch)
        if weight_sum != 1.0:
            raise ValidationError(
                branchset_node, "branchset weights don't sum up to 1.0"
            )
        filters = dict((filtername, branchset_node.get(filtername))
                       for filtername in self.FILTERS
                       if filtername in branchset_node.attrib)
        branchset = BranchSet(branches, uncertainty_type, filters)
        apply_to_branches = branchset_node.get('applyToBranches')
        if apply_to_branches:
            apply_to_branches = apply_to_branches.split()
            for branch_id in apply_to_branches:
                if not branch_id in self.branches:
                    raise ValidationError(
                        branchset_node,
                        'branch %s is not yet defined' % branch_id
                    )
                branch = self.branches[branch_id]
                if branch.child_branchset is not None:
                    raise ValidationError(
                        branchset_node,
                        'branch %s already has child branchset' % branch_id
                    )
                branch.child_branchset = branchset
                self.open_ends.remove(branch)
        else:
            for branch in self.open_ends:
                branch.child_branchset = branchset
            self.open_ends.clear()

        self.open_ends.update(branches)
        return branchset

    def validate_uncertainty_value(self, node, uncertainty_type, value):
        _float_re = r'(\+|\-)?(\d+|\d*\.\d+)'
        if uncertainty_type == 'sourceModel':
            # file should exist and be readable
            realpath = os.path.join(self.base_path, value)
            if not os.path.isfile(realpath):
                raise ValidationError(node, 'can not open file %r' % realpath)
            return realpath
        elif uncertainty_type == 'abGRAbsolute':
            if not re.match('^%s\s+%s$' % (_float_re, _float_re), value):
                raise ValidationError(
                    node, 'expected two float values separated by space'
                )
            return tuple(float(val) for val in value.split())
        else:
            if not re.match('^%s$' % _float_re, value):
                raise ValidationError(node, 'expected single float value')
            return float(value)

    def collect_source_model_data(self, filename):
        all_source_types = set('{%s}%s' % (self.NRML, tagname)
                               for tagname in self.SOURCE_TYPES)
        tectonic_region_type_tag = '{%s}tectonicRegion' % LogicTree.NRML
        tectonic_region_types = self.tectonic_region_types[filename] = set()
        source_ids = self.source_ids[filename] = set()
        source_types = self.source_types[filename] = set()
        nsprefix_length = len('{%s}' % self.NRML)
        eventstream = etree.iterparse(open(filename), tag='{%s}*' % self.NRML,
                                      schema=self.get_xmlschema())
        while True:
            try:
                event, node = next(eventstream)
            except StopIteration:
                break
            except etree.XMLSyntaxError as exc:
                raise ParsingError(filename, str(exc))
            if not node.tag in all_source_types:
                if node.tag == tectonic_region_type_tag:
                    tectonic_region_types.add(node.text)
            else:
                source_ids.add(
                    node.attrib['{http://www.opengis.net/gml}id']
                )
                source_types.add(node.tag[nsprefix_length:])

                # saving memory by removing already processed nodes.
                # see http://lxml.de/parsing.html#modifying-the-tree
                node.clear()
                parent = node.getparent()
                prev = node.getprevious()
                while prev is not None:
                    parent.remove(prev)
                    prev = node.getprevious()


if __name__ == '__main__':
    import sys
    base_path, filename = os.path.split(sys.argv[1])
    try:
        lt = LogicTree(base_path, filename)
        print lt.root
    except LogicTreeError as exc:
        sys.exit(str(exc))
