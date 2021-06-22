from src.topo import Topo

import pulp as pulp
import math
import os
import sys
import importlib
from jinja2 import Template
import json


class TopologyMapper(object):
    """Map input network topology to progarmmable switch"""

    def __init__(self, tm_input, port_num, specified_mapping = None):
        self.totalPortNum = port_num
        self.inputPhysicalPorts = tm_input['physical_ports']
        self.inputInternalPorts = tm_input['internal_ports']
        self.inputAllPorts = self.inputPhysicalPorts + self.inputInternalPorts
        self.inputPortSpeed = [n[2]['speed'] for n in self.inputAllPorts]
        self.specified_mapping = {} # {mapped_port: (port_group, sub_port, speed)}
        
    def pre_pm(self):
        if 4 * self.totalPortNum < len(self.inputAllPorts):
            return False

    def process_specified_mapping(self, specified_mapping):
        port_index = {}
        global_index = 0
        for (eswitch, eport, _) in self.inputAllPorts:
            port_index.setdefault(eswitch, {})
            port_index[eswitch][eport] = global_index
            global_index = global_index + 1

        for (eswitch, eport, port_str, speed) in specified_mapping:
            mapped_port = port_index[eswitch][eport]
            (port_group, sub_port) = port_str.split('/')
            self.specified_mapping[mapped_port] = (int(port_group), int(sub_port), speed)

    def run_pm(self):
        # print("\nStart Port-based mapping!")
        m = self.totalPortNum
        n = len(self.inputAllPorts)
        if self.pre_pm() is False:
            return False

        if m > n:
            m = n

        prob = pulp.LpProblem("Port mapping", pulp.LpMinimize)

        xi_vars = [pulp.LpVariable("ai_" + str(i), lowBound=0, upBound=1, cat=pulp.LpInteger) for i in range(m)]
        # 1*40G
        x1i_vars = [pulp.LpVariable("x1i_" + str(i), lowBound=0, upBound=1, cat=pulp.LpInteger) for i in range(m)]
        x1ik_vars = [pulp.LpVariable("X1i_" + str(i) + "_k_" + str(k), lowBound=0, upBound=1, cat=pulp.LpInteger)
                     for i in range(m) for k in range(n)]
        # 4*10G
        x3i_vars = [pulp.LpVariable("x3i_" + str(i), lowBound=0, upBound=1, cat=pulp.LpInteger) for i in range(m)]
        x3ik_vars = [pulp.LpVariable("X3i_" + str(i) + "_k_" + str(k), lowBound=0, upBound=1, cat=pulp.LpInteger)
                     for i in range(m) for k in range(n)]

        prob += sum(xi_vars[i] for i in range(m))
        # for i in range(m - 1):
        #     prob += (xi_vars[i] >= xi_vars[i + 1])
        for i in range(m):
            # each port i can be configured in one manner
            prob += (x1i_vars[i] + x3i_vars[i] == xi_vars[i])
            # each port i can be configured as 1 or 4 ports
            prob += (sum(x1ik_vars[k + i * n] for k in range(n)) <= 1 * x1i_vars[i])
            prob += (sum(x3ik_vars[k + i * n] for k in range(n)) <= 4 * x3i_vars[i])
        for k in range(n):
            # each interface k in S1 can be mapped to only one port
            prob += (sum(x1ik_vars[k + i * n] + x3ik_vars[k + i * n] for i in range(m)) == 1)

            # each interface k in S1 should be allocated >= b[k] bandwidth
            # if self.inputPortSpeed[k] > 10:
            prob += (sum(40 * x1ik_vars[k + i * n] + 10 * x3ik_vars[k + i * n] for i in range(m))
                     >= self.inputPortSpeed[k])

        # self.specified_mapping = {mapped_port: (port_group, sub_port, speed)}
        # self.specified_mapping = {0: (2, 1, 10), 1: (4, 0, 40)}
        for (k, (i, _, speed)) in self.specified_mapping.items():
            i = i - 1
            if speed == 10:
                prob += (x3i_vars[i] == 1)
                prob += (x3ik_vars[k + i * n] == 1)
            if speed == 40:
                prob += (x1i_vars[i] == 1)
                prob += (x1ik_vars[k + i * n] == 1)

        if prob.solve() != 1:
            print("Port Mapper Fails!")
            return False

        prob_output = [(v.name, v.varValue) for v in prob.variables() if v.varValue > 0]
        port_mapping = {}
        port_config = {}

        # {port_group: (sub_port, mapped_port, speed)}
        speed_map = {'1': 40, '3': 10}

        for (mapped_port, (port_group, sub_port, speed)) in self.specified_mapping.items():
            port_mapping.setdefault(port_group, [0, 1, 2, 3])
            port_str = str(port_group) + '/' + str(sub_port)
            port_config[port_str] = {'mapped_port': mapped_port,
                                     'config_speed': speed}
            port_mapping[port_group].remove(sub_port)

        for v in prob_output:
            if v[0].startswith('X'):
                [_, port_group, _, mapped_port] = v[0].split('_')
                port_group = int(port_group) + 1
                port_mapping.setdefault(port_group, [0, 1, 2, 3])
                mapped_port = int(mapped_port)
                config_speed = speed_map[v[0][1]]
                if mapped_port in self.specified_mapping.keys():
                    sub_port = self.specified_mapping[mapped_port][1]
                    port_str = str(port_group) + '/' + str(sub_port)
                    port_config[port_str]['config_speed'] = config_speed
                else:
                    sub_port = port_mapping[port_group][0]
                    port_str = str(port_group) + '/' + str(sub_port)
                    port_config[port_str] = {'mapped_port': mapped_port,
                                             'config_speed': config_speed}
                    port_mapping[port_group].pop(0)

        for k in port_config.keys():
            print("%s: " % k,end='')
            print(port_config[k])

        return port_config
