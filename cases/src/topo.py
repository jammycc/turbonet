#!/usr/bin/env python
"""@package topo

Network topology creation.

@author Brandon Heller (brandonh@stanford.edu)

This package includes code to represent network topologies.

A Topo object can be a topology database for NOX, can represent a physical
setup for testing, and can even be emulated with the Mininet package.
"""

from src.util import irange, natural, naturalSeq, build_graph, dijsktra_all
import os


class MultiGraph(object):
    """Utility class to track nodes and edges - replaces networkx.MultiGraph"""

    def __init__(self):
        self.node = {}
        self.edge = {}

    def add_node(self, node, attr_dict=None, **attrs):
        """Add node to graph
           attr_dict: attribute dict (optional)
           attrs: more attributes (optional)
           warning: updates attr_dict with attrs"""
        attr_dict = {} if attr_dict is None else attr_dict
        attr_dict.update(attrs)
        self.node[node] = attr_dict

    def update_node(self, node, attr_dict=None, **attrs):
        attr_dict = {} if attr_dict is None else attr_dict
        attr_dict.update(attrs)
        self.node[node].update(attr_dict)

    def add_edge(self, src, dst, key=None, attr_dict=None, **attrs):
        """Add edge to graph
           key: optional key
           attr_dict: optional attribute dict
           attrs: more attributes
           warning: udpates attr_dict with attrs"""
        attr_dict = {} if attr_dict is None else attr_dict
        attr_dict.update(attrs)
        self.node.setdefault(src, {})
        self.node.setdefault(dst, {})
        self.edge.setdefault(src, {})
        self.edge.setdefault(dst, {})
        self.edge[src].setdefault(dst, {})
        entry = self.edge[dst][src] = self.edge[src][dst]
        # If no key, pick next ordinal number
        if key is None:
            keys = [k for k in entry.keys() if isinstance(k, int)]
            key = max([0] + keys) + 1
        entry[key] = attr_dict
        return key

    def nodes(self, data=False):
        """Return list of graph nodes
           data: return list of ( node, attrs)"""
        return self.node.items() if data else self.node.keys()

    def edges_iter(self, data=False, keys=False):
        """Iterator: return graph edges, optionally with data and keys"""
        for src, entry in self.edge.items():
            for dst, entrykeys in entry.items():
                if src > dst:
                    # Skip duplicate edges
                    continue
                for k, attrs in entrykeys.items():
                    if data:
                        if keys:
                            yield src, dst, k, attrs
                        else:
                            yield src, dst, attrs
                    else:
                        if keys:
                            yield src, dst, k
                        else:
                            yield src, dst

    def edges(self, data=False, keys=False):
        """Return list of graph edges"""
        return list(self.edges_iter(data=data, keys=keys))

    def __getitem__(self, node):
        """Return link dict for given src node"""
        return self.edge[node]

    def __len__(self):
        """Return the number of nodes"""
        return len(self.node)

    def convertTo(self, cls, data=False, keys=False):
        """Convert to a new object of networkx.MultiGraph-like class cls
           data: include node and edge data
           keys: include edge keys as well as edge data"""
        g = cls()
        g.add_nodes_from(self.nodes(data=data))
        g.add_edges_from(self.edges(data=(data or keys), keys=keys))
        return g


def find_port(sw1, sw2, links):
    for (node1, node2, dic) in links:
        if node1 == sw1 and node2 == sw2:
            return dic['port1']
        elif node1 == sw2 and node2 == sw1:
            return dic['port2']
    return False


class Topo(object):
    """Data center network representation for structured multi-trees."""

    def __init__(self, *args, **params):
        """Topo object.
           Optional named parameters:
           hinfo: default host options
           sopts: default switch options
           lopts: default link options
           calls build()"""
        self.g = MultiGraph()
        self.hopts = params.pop('hopts', {})
        self.sopts = params.pop('sopts', {})
        self.lopts = params.pop('lopts', {})
        # ports[src][dst][sport] is port on dst that connects to src
        self.p = {}
        self.l3table_entries = []
        self.build(*args, **params)

    def build(self, *args, **params):
        """Override this method to build your topology."""
        pass

    def addNode(self, name, **opts):
        """Add Node to graph.
           name: name
           opts: node options
           returns: node name"""
        self.g.add_node(name, **opts)
        return name

    def addSwitch(self, name, **opts):
        """Convenience method: Add switch to graph.
           name: switch name
           opts: switch options
           returns: switch name"""
        if not opts and self.sopts:
            opts = self.sopts
        result = self.addNode(name, isSwitch=True, **opts)
        return result

    def addLink(self, node1, node2, port1, port2, key=None, **opts):
        """node1, node2: nodes to link together
           port1, port2: ports (optional)
           opts: link options (optional)
           returns: link info key"""
        if not opts and self.lopts:
            opts = self.lopts
        opts = dict(opts)
        link_id = len(self.links_list())
        opts.update(node1=node1, node2=node2, port1=port1, port2=port2, index=link_id)
        self.setPortAttrs(node1, port1, 'end', [node2, port2])
        self.setPortAttrs(node2, port2, 'end', [node1, port1])
        self.setPortAttrs(node1, port1, 'link', link_id)
        self.setPortAttrs(node2, port2, 'link', link_id)
        return self.g.add_edge(node1, node2, key, opts)

    def addPhysicalPort(self, switch, name, **opts):
        return self.addPort(switch, name, isPhysical=True, **opts)

    def addInternalPort(self, switch, name, **opts):
        return self.addPort(switch, name, isInternal=True, **opts)

    def addPort(self, switch, name, **opts):
        # Initialize if necessary
        ports = self.p
        ports.setdefault(switch, {})
        index = len(ports[switch])
        if name in ports[switch].keys():
            print("Port Exsits!")
            return False
        ports[switch][name] = {}
        ports[switch][name].update(opts)
        ports[switch][name]['index'] = index
        self.g.node[switch]['ports'] = index
        return name

    def setPortAttrs(self, switch, name, attr, value):
        self.p[switch][name][attr] = value

    def nodes(self, sort=False, data=False):
        """Return nodes in graph"""
        if sort:
            return self.sorted(self.g.nodes(data))
        else:
            return self.g.nodes(data)

    def isInternal(self, n):
        a = self.g.node[n]
        return a.get('isInternal', False)

    def isSwitch(self, n):
        """Returns true if node is a switch."""
        return self.g.node[n].get('isSwitch', False)

    def iterLinks(self, withKeys=False, withInfo=False):
        """Return links (iterator)
           withKeys: return link keys
           withInfo: return link info
           returns: list of ( src, dst [,key, info ] )"""
        for _src, _dst, key, info in self.g.edges_iter(data=True, keys=True):
            node1, node2 = info['node1'], info['node2']
            if withKeys:
                if withInfo:
                    yield node1, node2, key, info
                else:
                    yield node1, node2, key
            else:
                if withInfo:
                    yield node1, node2, info
                else:
                    yield node1, node2

    def iterPorts(self, info=False):
        """Iterator: return graph edges, optionally with data and keys"""
        for switch, entry in self.p.items():
            for port, entrykeys in entry.items():
                """for k, attrs in entrykeys.items():
                    if info:
                        yield (switch, port, k, attrs)
                    else:
                        yield (switch, port)"""
                if info:
                    yield switch, port, entrykeys
                else:
                    yield switch, port

    def ports(self, sort=True, info=False):
        ports = list(self.iterPorts(info))
        if not sort:
            return ports
        return sorted(ports, key=(lambda l: naturalSeq(l[:2])))

    def _linkEntry(self, src, dst, key=None):
        """Helper function: return link entry and key"""
        entry = self.g[src][dst]
        if key is None:
            key = min(entry)
        return entry, key

    def linkInfo(self, src, dst, key=None):
        """Return link metadata dict"""
        entry, key = self._linkEntry(src, dst, key)
        return entry[key]

    def setlinkInfo(self, src, dst, info, key=None):
        """Set link metadata dict"""
        entry, key = self._linkEntry(src, dst, key)
        entry[key] = info

    def nodeInfo(self, name):
        """Return metadata (dict) for node"""
        return self.g.node[name]

    def setNodeInfo(self, name, info):
        """Set metadata (dict) for node"""
        self.g.node[name] = info

    def convertTo(self, cls, data=True, keys=True):
        """Convert to a new object of networkx.MultiGraph-like class cls
           data: include node and edge data (default True)
           keys: include edge keys as well as edge data (default True)"""
        return self.g.convertTo(cls, data=data, keys=keys)

    @staticmethod
    def sorted(items):
        """Items sorted in natural (i.e. alphabetical) order"""
        return sorted(items, key=natural)

    def switches_list(self, info=False):
        """Return switches.
           sort: sort switches alphabetically
           returns: dpids list of dpids"""
        if info is False:
            return [n for n in self.nodes(sort=True, data=info) if self.isSwitch(n)]
        else:
            return [n for n in self.nodes(sort=True, data=info) if self.isSwitch(n[0])]

    def physicalPorts_list(self, info=False):
        ports = self.ports(info=True)
        return [n if info else n[:1] for n in ports if n[2].get('isPhysical')]

    def internalPorts_list(self, info=False):
        ports = self.ports(info=True)
        return [n if info else n[:1] for n in ports if n[2].get('isInternal')]

    def links_list(self, sort=True, withKeys=False, withInfo=False):
        """Return links
           sort: sort links alphabetically, preserving (src, dst) order
           withKeys: return link keys
           withInfo: return link info
           returns: list of ( src, dst [,key, info ] )"""
        links = list(self.iterLinks(withKeys, withInfo))
        if not sort:
            return links
        # Ignore info when sorting
        tupleSize = 3 if withKeys else 2
        return sorted(links, key=(lambda l: naturalSeq(l[:tupleSize])))

    def add_fixed_entry(self, switch, dip, mask, port):
        self.l3table_entries.append((switch, dip, mask, port))

    def print_l3_entries(self):
        for k in self.l3table_entries:
            print(k)

    def get_dijsktra_routing(self):
        print("Set diksktra routing!")
        nodes = self.switches_list(info=False)
        links = self.links_list(sort=True, withInfo=True)
        graph = build_graph(nodes, links)
        shortest_path = dijsktra_all(graph)
        self.set_dijkstra(shortest_path, nodes, links)

    def set_dijkstra(self, shortest_path, nodes, links):
        all_ports = self.p
        for sw1 in nodes:
            for (sw2, sw2_ports) in all_ports.items():
                for (sw2_port, spec) in sw2_ports.items():
                    if 'ip' in spec.keys():
                        dip = spec['ip'][0]
                        mask = spec['ip'][1]
                        if sw1 == sw2:
                            egress_port = sw2_port
                        else:
                            next_sw = shortest_path[nodes.index(sw1)][nodes.index(sw1)][nodes.index(sw2)][0]
                            egress_port = find_port(sw1, nodes[next_sw], links)
                        if egress_port is False:
                            return False
                        self.add_fixed_entry(sw1, dip, mask, egress_port)

    def print_topo(self):
        topo_info = {"switches": self.switches_list(info=False),
                "links": self.links_list(sort=True, withInfo=True),
                "ports": self.p,
                "physical_ports": self.physicalPorts_list(info=True),
                "internal_ports": self.internalPorts_list(info=True)}
        for k in topo_info.keys():
            print("%s: " % k,end='')
            print(topo_info[k])
        return topo_info
