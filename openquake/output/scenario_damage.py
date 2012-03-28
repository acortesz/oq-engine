# Copyright (c) 2010-2012, GEM Foundation.
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake.  If not, see <http://www.gnu.org/licenses/>.

from lxml import etree

from openquake import xml


class DmgDistPerAssetXMLWriter(object):

    def __init__(self, path, end_branch_label, damage_states):
        self.path = path
        self.damage_states = damage_states
        self.end_branch_label = end_branch_label

        # < /nrml> element
        self.root = None

        # < /dmgDistPerAsset> element
        self.dmg_dist_el = None

    def serialize(self, assets_data):
        if assets_data is None or not len(assets_data):
            raise RuntimeError(
                "empty damage distributions are not supported by the schema.")

        # contains the set of </ DDNode> elements indexed per site
        dd_nodes = {}

        # contains the set of </ asset> elements indexed per asset ref
        asset_nodes = {}

        with open(self.path, "w") as fh:
            self._create_root_elems()

            for asset_data in assets_data:
                site = asset_data.exposure_data.site
                asset_ref = asset_data.exposure_data.asset_ref

                dd_node_el = dd_nodes.get(site.wkt, None)

                if dd_node_el is None:
                    dd_node_el = etree.SubElement(self.dmg_dist_el, "DDNode")
                    site_el = etree.SubElement(dd_node_el, xml.RISK_SITE_TAG)

                    point_el = etree.SubElement(site_el, xml.GML_POINT_TAG)
                    point_el.set(xml.GML_SRS_ATTR_NAME, xml.GML_SRS_EPSG_4326)

                    pos_el = etree.SubElement(point_el, xml.GML_POS_TAG)
                    pos_el.text = "%s %s" % (site.x, site.y)

                    dd_nodes[site.wkt] = dd_node_el

                asset_node_el = asset_nodes.get(asset_ref, None)

                if asset_node_el is None:
                    asset_node_el = etree.SubElement(dd_node_el, "asset")
                    asset_node_el.set("assetRef", asset_ref)

                    asset_nodes[asset_ref] = asset_node_el

                ds_node = etree.SubElement(asset_node_el, "damage")
                ds_node.set("ds", asset_data.dmg_state)
                ds_node.set("mean", str(asset_data.mean))
                ds_node.set("stddev", str(asset_data.stddev))

            fh.write(etree.tostring(
                self.root, pretty_print=True, xml_declaration=True,
                encoding="UTF-8"))

    def _create_root_elems(self):
        self.root = etree.Element("nrml", nsmap=xml.NSMAP)
        self.root.set("%sid" % xml.GML, "n1")

        self.dmg_dist_el = etree.SubElement(self.root, "dmgDistPerAsset")
        self.dmg_dist_el.set("endBranchLabel", self.end_branch_label)

        dmg_states = etree.SubElement(self.dmg_dist_el, "damageStates")
        dmg_states.text = " ".join(self.damage_states)
