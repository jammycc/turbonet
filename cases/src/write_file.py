import math
import os
import sys
import importlib
from jinja2 import Template
import json


def generate_define_file(routing, metric, function):
    cur_dir = os.path.dirname(__file__)
    print(cur_dir)
    # open define.p4
    define_file = os.path.join(cur_dir, 'src/p4src/common/define.p4')
    f_define = open(define_file, 'w')

    f_define.write("#ifndef _DEFINE_H_"
                   "\n#define _DEFINE_H_")

    define_all = [routing, metric, function]
    for define_type in define_all:
        f_define.write('\n')
        for define in define_type:
            f_define.write("\n#define " + define)

    f_define.write('\n\n#endif /* _DEFINE_H_ */')

    f_define.close()


def generate_output(topo_input, topology_mapping_input, routing_input):
    switch_list = topo_input['switches']
    link_list = topo_input['links']
    port_dict = topo_input['ports']
    physical_port_list = topo_input['physical_ports']
    internal_port_list = topo_input['internal_ports']
    port_list = physical_port_list + internal_port_list

    links = []
    # [(eswitch_id1, eport_id1, eswitch_id2, eport_id2)]
    # e.g., [(1,1,2,0),(2,1,3,0)]
    for (_, _, link) in link_list:
        links.append((switch_list.index(link['node1']),
                      port_dict[link['node1']][link['port1']]['index'],
                      switch_list.index(link['node2']),
                      port_dict[link['node2']][link['port2']]['index']))

    port_config = {}
    # port_config = {port_str: config}
    # e.g., {'2/0': {'loopback_mode': False, 'speed': "10Gbps", 'eswitch_id': 1, 'eport_id': 0},
    for (port_str, entry) in topology_mapping_input.items():
        mapped_port_id = entry['mapped_port']
        (eswitch, eport, port_spec) = port_list[mapped_port_id]
        port_config[port_str] = {
            'eswitch_id': switch_list.index(eswitch),
            'eport_id': port_dict[eswitch][eport]['index'],
            'loopback_mode': port_spec.get('isInternal', False),
            'shaped_speed': port_spec['speed'],
            'config_speed': entry['config_speed']
        }
    ipv4_entries = {}
    if routing_input is not None:

        # {eswitch_id: entries}
        # {1:[('10.0.1.1', 24, 1), ('10.0.0.1', 24, 0)], 2/:[('10.0.1.1', 24, 1), ('10.0.0.1', 24, 0)]}
        for (eswitch, ipv4, prefix, eport) in routing_input:
            eswitch_id = switch_list.index(eswitch)
            ipv4_entries.setdefault(eswitch_id, [])
            ipv4_entries[eswitch_id].append((ipv4, prefix, port_dict[eswitch][eport]['index']))
    print("Writing File:")
    print("    links: ", end='')
    print(links)
    print("    port_config: ", end='')
    print(port_config)
    print("    ipv4_entries: ", end='')
    print(ipv4_entries)
    return {'links': links, 'port_config': port_config, 'ipv4_entries': ipv4_entries}
