#!/usr/bin/python

from src.topo import *
from src.mapper import TopologyMapper
from src.write_file import *
import os


class FatTreeTopo(Topo):
    """
    FatTree
    """

    def build(self, k=4, speed=10):
        self.name = "FatTree"
        self.specified_mapping = {}
        self.k = k
        self.speed = speed
        self.edge = []
        self.aggr = []
        self.core = []
        edge_per_pod = int(self.k / 2)
        edge_servers = int(self.k / 2)
        edge_aggrs = int(self.k / 2)
        aggr_per_pod = int(self.k / 2)
        aggr_cores = int(self.k / 2)
        core = int(self.k * self.k / 4)
        for i in range(self.k):
            for j in range(edge_per_pod):
                self.edge.append(self.addSwitch('edge_%d_%d' % (i, j)))
            for j in range(aggr_per_pod):
                self.aggr.append(self.addSwitch('aggr_%d_%d' % (i, j)))
        for i in range(core):
            self.core.append(self.addSwitch('core_%d' % i))

        for i in range(self.k):
            for j in range(edge_per_pod):
                edge_switch = self.edge[i * edge_per_pod + j]
                # host-edge
                for m in range(edge_servers):
                    p = self.addPhysicalPort(edge_switch, 'edge_host_%d_%d_%d' % (i, j, m), speed=self.speed)
                    # ip = '192.%d.%d.1' % (i, j * edge_servers + m)
                    # self.setPortAttrs(edge_switch, p, 'ip', [ip, 24])
                # edge-aggr
                for m in range(edge_aggrs):
                    aggr_switch = self.aggr[i * edge_per_pod + m]
                    p1 = self.addInternalPort(edge_switch, 'edge_aggr_%d_%d_%d' % (i, j, m), speed=self.speed)
                    p2 = self.addInternalPort(aggr_switch, 'aggr_edge_%d_%d_%d' % (i, j, m), speed=self.speed)
                    if i == 0 and j == 0:
                        self.addLink(edge_switch, aggr_switch, p1, p2)
                    elif i == 0 and j == 1:
                        self.addLink(edge_switch, aggr_switch, p1, p2)
                    else:
                        self.addLink(edge_switch, aggr_switch, p1, p2)

            for j in range(aggr_per_pod):
                # aggr-core
                aggr_switch = self.aggr[i * aggr_per_pod + m]
                for m in range(aggr_cores):
                    core_switch = self.core[j * aggr_cores + m]
                    p1 = self.addInternalPort(aggr_switch, 'aggr_core_%d_%d_%d' % (i, j, m), speed=self.speed)
                    p2 = self.addInternalPort(core_switch, 'core_aggr_%d_%d_%d' % (i, j, m), speed=self.speed)
                    self.addLink(aggr_switch, core_switch, p1, p2)

        # ip = '10.%d.%d.1' % (i, j * edge_servers + m)
        self.setPortAttrs('edge_0_0', 'edge_host_0_0_0', 'ip', ['10.0.1.0', 24])
        self.setPortAttrs('edge_3_1', 'edge_host_3_1_1', 'ip', ['10.0.2.1', 24])

    def set_routing_entries(self):
        self.get_dijsktra_routing()

    def set_specified_mapping(self):
        # specical process
        # specify some ports as specific Tofino ports
        # e.g., s1-p1 should be '2/1' (137), and s3-p3 should be '4/0' 152
        self.specified_mapping = [('edge_0_0', 'edge_host_0_0_0', '2/1', 10),
                                  ('edge_3_1', 'edge_host_3_1_1', '4/0', 40)]


class ThreeSwitchesTopo(Topo):
    """
    2 hosts connected by 3 switches
    """

    def build(self):
        self.specified_mapping = {}
        self.name = "ThreeSwitches"
        self.addSwitch('s1')
        self.addSwitch('s2')
        self.addSwitch('s3')
        port1 = self.addPhysicalPort('s1', 'p1', speed=10)

        port12 = self.addInternalPort('s1', 'p12', speed=10)
        port21 = self.addInternalPort('s2', 'p21', speed=10)
        self.addLink('s1', 's2', port12, port21)
        port23 = self.addInternalPort('s2', 'p23', speed=10)
        port32 = self.addInternalPort('s3', 'p32', speed=10)
        self.addLink('s2', 's3', port23, port32)

        port3 = self.addPhysicalPort('s3', 'p3', speed=40)

    def set_routing_entries(self):
        self.l3table_entries = [['s1', '10.0.1.0', 24, 'p1'],
                                ['s1', '10.0.2.0', 24, 'p12'],
                                ['s2', '10.0.1.0', 24, 'p21'],
                                ['s2', '10.0.2.0', 24, 'p23'],
                                ['s3', '10.0.1.0', 24, 'p32'],
                                ['s3', '10.0.2.0', 24, 'p3']]

    def set_specified_mapping(self):
        # specical process
        # specify some ports as specific Tofino ports
        # e.g., s1-p1 should be '2/1' (137), and s3-p3 should be '4/0' 152
        self.specified_mapping = [('s1', 'p1', '2/1', 10), ('s3', 'p3', '4/0', 40)]


PORT_NUM = 32


def run():
    # 1. Create network and run the CLI
    print("\n************ Establish Topology *************")
    topology = FatTreeTopo(k=4)
    # topology = ThreeSwitchesTopo()
    topology_output = topology.print_topo()

    # 2. Topology Mapper
    print("\n************ Map Topology *************")
    topology_mapper = TopologyMapper(topology_output, PORT_NUM)
    # Process specified mapping
    topology.set_specified_mapping()
    topology_mapper.process_specified_mapping(topology.specified_mapping)
    # Start topology mappig
    tm_output = topology_mapper.run_pm()
    if tm_output is False:
        return

    # 3. Set Routing Entries
    print("\n************ Set Routing Entries *************")
    topology.set_routing_entries()
    routing_output = topology.l3table_entries
    topology.print_l3_entries()

    '''
    4. Metric Mapper
    metric_mapper = MetricMapper(mm_input)
    metric_mapper.write_file()
    
    # 5. Function Mapper
    function_mapper = FunctionMapper(fm_input)
    function_mapper.write_file()
    '''

    # 6. Write File
    print("\n************ Write outputs to file *************")
    write_output = generate_output(topology_output, tm_output, routing_output)
    write_file(write_output, topology.name)


def write_file(content, name):
    cur_dir = os.path.dirname(__file__)
    # folder_path = os.path.join(cur_dir, NAME)
    file_path = cur_dir + '/examples/' + name + '.log'

    f_port = open(file_path, 'w')
    f_port.write(str(content))
    f_port.close()
    print("Success!! ^_^")


if __name__ == '__main__':
    run()
