#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import json
import time
import signal
import ipaddress
import os

from p4_runtime.runtime import *

BURST_SIZE = 16384


class TurboNet():
    def __init__(self, example):
        self.port_map = {}

        # port_config = {port_str: config}
        # config = {loopback_mode: xx;
        #           shaped_speed: xx;
        #           config_speed: xx;
        #           eswitch_id: xx;
        #           eport_id: xx;} 
        self.port_config = {}
        
        # [(eswitch_id1, eport_id1, eswitch_id2, eport_id2)]
        self.links = []

        # {eswitch_id: entries}
        # entries = [(dip, mask, eport_id)]
        self.ipv4_entries = {}
        
        self.example = example

    def read_file(self):
        print("\n********************** read file **********************")

        example = self.example
        cur_dir = os.path.dirname(__file__)
        file_dir = os.path.join(cur_dir, "../cases/examples/" + example)
        f = open(file_dir, 'r')
        file_content = eval(f.read())
        f.close()

        self.links = file_content['links']
        self.port_config = file_content['port_config']
        self.ipv4_entries = file_content['ipv4_entries']

        print(self.port_config)
        print(self.links)
        print(self.ipv4_entries)
   
    def add_port(self, port, loopback, shape_speed, config_speed):
        port = port_to_int(port)
        self.port_map[port] = [port, loopback, shape_speed, config_speed]
        # speed
        if config_speed == 10:
            self.runtime.setup_10g_port(port)
        elif config_speed == 25:
            self.runtime.setup_25g_port(port)
        elif config_speed == 40:
            self.runtime.setup_40g_port(port)
        # loopback mode
        if loopback == True:
            self.runtime.setup_loopback_port(port)
        # port shaping
        if shape_speed < config_speed:
            self.runtime.set_port_shaping(port, False, BURST_SIZE, shape_speed)

        self.runtime.complete_operations()

    def set_up_ports(self):
        print("\n********************** set up ports **********************")
        for port, config in self.port_config.items():
            self.add_port(port, config['loopback_mode'], config['shaped_speed'], config['config_speed'])

    def set_up_elink(self):
        for (port, config) in self.port_config.items():
            port_num = port_to_int(port)
            eswitch_id = config['eswitch_id']
            eport_id = config['eport_id']
            if (config['loopback_mode'] == True):
                self.runtime.add_table_entry('get_elink', 'get_next_elink', (eswitch_id, eport_id, ), (port_num, ))
            else:
                self.runtime.add_table_entry('get_eswitch_from_plink', 'add_ehdr', (port_num, ), (eswitch_id, eport_id))
                self.runtime.add_table_entry('get_elink', 'remove_ehdr', (eswitch_id, eport_id, ), (port_num, ))

        for (eswitch_id1, eport_id1, eswitch_id2, eport_id2) in self.links:
            self.runtime.add_table_entry('get_eswitch_from_elink', 'get_eswitch', (eswitch_id2, eport_id2, ), (eswitch_id1, eport_id1, ))
            self.runtime.add_table_entry('get_eswitch_from_elink', 'get_eswitch', (eswitch_id1, eport_id1, ), (eswitch_id2, eport_id2, ))
            
    def set_up_eswitch(self):
        for (eswitch_id, entries) in self.ipv4_entries.items():
            for (dip, mask, eport_id) in entries:
                dip = ipv4Addr_to_i32(dip)
                self.runtime.add_table_entry('ipv4_forward', 'set_egress_port', (eswitch_id, dip, mask, ), (eport_id, ))    

    def set_up_topology(self):
        print("\n********************** add table entries **********************")
        self.set_up_elink()
        self.set_up_eswitch()
        self.runtime.set_default_entry('get_elink', 'remove_ehdr', (152,))

    def dump_table_entries(self):
        print("\n********************** dump table entries **********************")

        for (table_name, entries) in self.runtime.table_entry_for_dump.items():
            print(table_name)
            print(entries)

    def start(self):
        self.runtime = TofinoRuntime('turbonet')
        self.runtime.start()
        self.runtime.clean_up_all_ports()
        self.runtime.clean_up_table('get_eswitch_from_elink')
        self.runtime.clean_up_table('get_eswitch_from_plink')
        self.runtime.clean_up_table('get_elink')
        self.runtime.clean_up_table('ipv4_forward')
        
        self.read_file()

        self.set_up_ports()
        self.set_up_topology()
        self.dump_table_entries()
        
    def stop(self):
        time.sleep(1)
        self.runtime.stop()
        print("stop")
        
    def validate_port(self, port):
        return validate_port(port)

config_file = sys.argv[1] + '.log'
turbonet = TurboNet(config_file) # ("ThreeSwitches.log")
turbonet.start()