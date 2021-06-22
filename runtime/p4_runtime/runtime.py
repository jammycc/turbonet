#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import importlib
import os
import json
import struct
import socket

if 'SDE_INSTALL' not in os.environ:
    print("SDE_INSTALL is not set. Exit.")
    exit(1)

env_dist = os.environ
sys.path.append(env_dist['SDE_INSTALL'] + "/lib/python2.7/site-packages/tofino/")

from res_pd_rpc.ttypes import *
from conn_mgr_pd_rpc.ttypes import *
from conn_mgr_pd_rpc import *
from mirror_pd_rpc.ttypes import *
from mirror_pd_rpc import *
from pal_rpc.ttypes import *
from pal_rpc import *
from tm_api_rpc import tm
from tm_api_rpc.ttypes import *

from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol, TMultiplexedProtocol

g_port_dict = {
    '1/0': 128, '1/1': 129, '1/2': 130, '1/3': 131,
    '2/0': 136, '2/1': 137, '2/2': 138, '2/3': 139,
    '3/0': 144, '3/1': 145, '3/2': 146, '3/3': 147,
    '4/0': 152, '4/1': 153, '4/2': 154, '4/3': 155,
    '5/0': 160, '5/1': 161, '5/2': 162, '5/3': 163,
    '6/0': 168, '6/1': 169, '6/2': 170, '6/3': 171,
    '7/0': 176, '7/1': 177, '7/2': 178, '7/3': 179,
    '8/0': 184, '8/1': 185, '8/2': 186, '8/3': 187,
    '9/0': 60 , '9/1': 61 , '9/2': 62 , '9/3': 63 ,
    '10/0': 52, '10/1': 53, '10/2': 54, '10/3': 55,
    '11/0': 44, '11/1': 45, '11/2': 46, '11/3': 47,
    '12/0': 36, '12/1': 37, '12/2': 38, '12/3': 39,
    '13/0': 28, '13/1': 29, '13/2': 30, '13/3': 31,
    '14/0': 20, '14/1': 21, '14/2': 22, '14/3': 23,
    '15/0': 12, '15/1': 13, '15/2': 14, '15/3': 15,
    '16/0': 4,  '16/1': 5,  '16/2': 6,  '16/3': 7,
    '17/0': 0,  '17/1': 1,  '17/2': 2,  '17/3': 3,
    '18/0': 8,  '18/1': 9,  '18/2': 10, '18/3': 11,
    '19/0': 16, '19/1': 17, '19/2': 18, '19/3': 19,
    '20/0': 24, '20/1': 25, '20/2': 26, '20/3': 27,
    '21/0': 32, '21/1': 33, '21/2': 34, '21/3': 35,
    '22/0': 40, '22/1': 41, '22/2': 42, '22/3': 43,
    '23/0': 48, '23/1': 49, '23/2': 50, '23/3': 51,
    '24/0': 56, '24/1': 57, '24/2': 58, '24/3': 59,
    '25/0': 188,'25/1': 189,'25/2': 190,'25/3': 191,
    '26/0': 180,'26/1': 181,'26/2': 182,'26/3': 183,
    '29/0': 148,'29/1': 149,'29/2': 150,'29/3': 151,
    '30/0': 156,'30/1': 157,'30/2': 158,'30/3': 159,
    '32/0': 140,'32/1': 141,'32/2': 142,'32/3': 143
}

def mirror_session(mir_type, mir_dir, sid, egr_port=0, egr_port_v=False,
                   egr_port_queue=0, packet_color=0, mcast_grp_a=0,
                   mcast_grp_a_v=False, mcast_grp_b=0, mcast_grp_b_v=False,
                   max_pkt_len=0, level1_mcast_hash=0, level2_mcast_hash=0,
                   cos=0, c2c=0, extract_len=0, timeout=0, int_hdr=[]):
  return MirrorSessionInfo_t(mir_type,
                             mir_dir,
                             sid,
                             egr_port,
                             egr_port_v,
                             egr_port_queue,
                             packet_color,
                             mcast_grp_a,
                             mcast_grp_a_v,
                             mcast_grp_b,
                             mcast_grp_b_v,
                             max_pkt_len,
                             level1_mcast_hash,
                             level2_mcast_hash,
                             cos,
                             c2c,
                             extract_len,
                             timeout,
                             int_hdr,
                             len(int_hdr))

def hex_to_i16(h):
    x = int(h)
    if (x > 0x7FFF): x-= 0x10000
    return x

def i16_to_hex(h):
    x = int(h)
    if (x & 0x8000): x+= 0x10000
    return x

def hex_to_i32(h):
    x = int(h)
    if (x > 0x7FFFFFFF): x-= 0x100000000
    return x

def i32_to_hex(h):
    x = int(h)
    if (x & 0x80000000): x+= 0x100000000
    return x

def hex_to_byte(h):
    x = int(h)
    if (x > 0x7F): x-= 0x100
    return x

def byte_to_hex(h):
    x = int(h)
    if (x & 0x80): x+= 0x100
    return x

def uint_to_i32(u):
    if (u > 0x7FFFFFFF): u-= 0x100000000
    return u

def i32_to_uint(u):
    if (u & 0x80000000): u+= 0x100000000
    return u

def char_to_uchar(x):
    if (x >= 0):
        return x
    return 256 + x

def bytes_to_string(byte_array):
    form = 'B' * len(byte_array)
    return struct.pack(form, *byte_array)

def string_to_bytes(string):
    form = 'B' * len(string)
    return list(struct.unpack(form, string))

def macAddr_to_string(addr):
    byte_array = [int(b, 16) for b in addr.split(':')]
    return bytes_to_string(byte_array)

def ipv4Addr_to_i32(addr):
    byte_array = [int(b) for b in addr.split('.')]
    res = 0
    for b in byte_array: res = res * 256 + b
    return uint_to_i32(res)

def stringify_macAddr(addr):
    return ':'.join('%02x' % char_to_uchar(x) for x in addr)

def i32_to_ipv4Addr(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))

def ipv6Addr_to_string(addr):
    return (str(socket.inet_pton(socket.AF_INET6, addr)))

def port_to_int(port):
    return g_port_dict[port]

def int_to_port(port_num):
    for port in g_port_dict:
        if g_port_dict[port] == port_num:
            return port

def validate_port(port):
    if port in g_port_dict:
        return True
    else:
        return False

TOFINO_MODE = 1
TOFINO_MODEL_MODE = 2

class TofinoRuntime():
    def __init__(self, program_name, mode = TOFINO_MODE):
        transport = TSocket.TSocket('202.112.237.111', 9090)
        # transport = TSocket.TSocket('localhost', 9090)
        self.transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        self.program_name = program_name
        sys.path.append(env_dist['SDE_INSTALL'] + "/lib/python2.7/site-packages/tofinopd/%s/p4_pd_rpc"%self.program_name)
        
        self.pd_lib = importlib.import_module(self.program_name)
        self.pd_types = importlib.import_module('ttypes')
        self.mode = mode

        self.dev = 0
        self.dev_tgt = DevTarget_t(0, -1)

        pd_protocol = TMultiplexedProtocol.TMultiplexedProtocol(protocol, self.program_name)
        self.pd_client = self.pd_lib.Client(pd_protocol)

        conn_protocol = TMultiplexedProtocol.TMultiplexedProtocol(protocol, "conn_mgr")
        self.conn_client = conn_mgr.Client(conn_protocol)

        mir_protocol = TMultiplexedProtocol.TMultiplexedProtocol(protocol, 'mirror')
        self.mir_client = mirror.Client(mir_protocol)
        
        pal_protocol = TMultiplexedProtocol.TMultiplexedProtocol(protocol, "pal")
        self.pal_client = pal.Client(pal_protocol)

        tm_protocol = TMultiplexedProtocol.TMultiplexedProtocol(protocol, "tm")
        self.tm_client = tm.Client(tm_protocol)

        self.table_entry_map = {}
        self.table_entry_for_dump = {}

    def start(self):
        self.transport.open()
        self.sess_hdl = 0 # self.conn_client.client_init()
            
    def stop(self):
        self.conn_client.client_cleanup(self.sess_hdl)
        self.transport.close()

    def begin_batch(self):
        self.conn_client.begin_batch(self.sess_hdl)

    def end_batch(self):
        self.conn_client.end_batch(self.sess_hdl, False)

    def complete_operations(self):
        self.conn_client.complete_operations(self.sess_hdl)

    def add_table_entry(self, table_name, action_name, 
                        match_fields, action_parameters=None, priority=None):
        if table_name not in self.table_entry_map:
            self.table_entry_map[table_name] = {}
            self.table_entry_for_dump[table_name] = {}
        
        if self.pd_client is None:
            print('self.pd_client in P4 controller should not be None.')
            return
        command_str = "self.pd_types.%s_%s_match_spec_t" % (self.program_name, table_name)
        match_spec = eval(command_str)(*match_fields)

        action_spec = None
        if action_parameters != None and len(action_parameters) > 0:
            command_str = "self.pd_types.%s_%s_action_spec_t" % (self.program_name, action_name)
            action_spec = eval(command_str)(*action_parameters)

        command_str = "self.pd_client."
        if action_spec is None:
            if priority is None:
                command_str += "%s_table_add_with_%s(self.sess_hdl, self.dev_tgt, match_spec)" % (table_name, action_name)
            else:
                command_str += "%s_table_add_with_%s(self.sess_hdl, self.dev_tgt, match_spec, %d)" % (table_name, action_name, priority)
        else:
            if priority is None:
                command_str += "%s_table_add_with_%s(self.sess_hdl, self.dev_tgt, match_spec, action_spec)" % (table_name, action_name)
            else:
                command_str += "%s_table_add_with_%s(self.sess_hdl, self.dev_tgt, match_spec, %d, action_spec)" % (table_name, action_name, priority)
        # print(command_str)
        self.table_entry_map[table_name][match_fields] = eval(command_str)
        self.table_entry_for_dump[table_name][match_fields] = [action_name, action_parameters]
        return self.table_entry_map[table_name][match_fields] 
    
    def set_default_entry(self, table_name, action_name, action_parameters):
        action_spec = None
        if len(action_parameters) > 0:
            command_str = "self.pd_types.%s_%s_action_spec_t"%(self.program_name, action_name)
            action_spec = eval(command_str)(*action_parameters)
        
        command_str = 'self.pd_client.'
        if action_spec is None:
            command_str += "%s_set_default_action_%s(self.sess_hdl, self.dev_tgt)" % (table_name, action_name)
        else:
            command_str += "%s_set_default_action_%s(self.sess_hdl, self.dev_tgt, action_spec)" % (table_name, action_name)
        return eval(command_str)

    def clean_up_table(self, table_name):
        command_str = 'self.pd_client.' + table_name
        num_entries = self.get_table_size(table_name)
        if num_entries == 0:
            return
        hdl = eval(command_str + '_get_first_entry_handle')(self.sess_hdl, self.dev_tgt)
        if num_entries > 1:
            hdls = eval(command_str + '_get_next_entry_handles')(self.sess_hdl,
                                                                self.dev_tgt, 
                                                                hdl, 
                                                                num_entries - 1)
            hdls.insert(0, hdl)
        else:
            hdls = [hdl]
        # delete the table entries
        for hdl in hdls:
            entry = eval(command_str + '_get_entry')(self.sess_hdl,
                                                    self.dev_tgt.dev_id, 
                                                    hdl, 
                                                    True)
            eval(command_str + '_table_delete')(self.sess_hdl,
                                               self.dev_tgt.dev_id, 
                                               hdl)

    def del_table_entry(self, table_name, match_fields):
        if table_name not in self.table_entry_map:
            return
        
        if match_fields not in self.table_entry_map[table_name]:
            return

        command_str = 'self.pd_client.' + table_name + '_table_delete'
        eval(command_str)(self.sess_hdl, self.dev_tgt.dev_id, self.table_entry_map[table_name][match_fields])
        self.table_entry_map[table_name].pop(match_fields)

    def get_table_size(self, table_name):
        command_str = 'self.pd_client.' + table_name
        num_entries = eval(
            command_str + '_get_entry_count')(self.sess_hdl, self.dev_tgt)
        return num_entries

    def read_counter(self, name, index):
        command_str = "self.pd_types.%s_counter_flags_t"%self.program_name
        flag = eval(command_str)(1)

        command_str = "self.pd_client.counter_read_%s"%name
        ret_val = eval(command_str)(self.sess_hdl, self.dev_tgt, index, flag)
        return ret_val

    def cleanup_counter(self, name, index):
        command_str = "self.pd_types.%s_counter_value_t"%self.program_name
        value = eval(command_str)(0, 0)
        
        command_str = "self.pd_client.counter_write_%s"%name
        eval(command_str)(self.sess_hdl, self.dev_tgt, index, value)
    
    def setup_port(self, port, speed, 
                    an = None, fec = pal_fec_type_t.BF_FEC_TYP_NONE):
        if isinstance(port, int) == False:
            port = g_port_dict[port]
        self.pal_client.pal_port_add(self.dev, port, speed, fec)
        if an is not None:
            self.pal_client.pal_port_an_set(self.dev, port, an)
        else:
            self.pal_client.pal_port_an_set(self.dev, port, 2)
        self.pal_client.pal_port_enable(self.dev, port)
    
    def setup_loopback_port(self, port, loopback_mode = 1):
        self.pal_client.pal_port_loopback_mode_set(self.dev, port, loopback_mode)

    def set_port_shaping(self, port, flag, burst_size, speed):
        self.tm_client.tm_enable_port_shaping(self.dev, port)
        self.tm_client.tm_set_port_shaping_rate(self.dev, port, flag, burst_size, speed*1024*1024)

    def setup_10g_port(self, port, 
                        an = None, fec = pal_fec_type_t.BF_FEC_TYP_NONE):
        self.setup_port(port, pal_port_speed_t.BF_SPEED_10G, an, fec)

    def setup_25g_port(self, port, 
                        an = None, fec = pal_fec_type_t.BF_FEC_TYP_NONE):
        self.setup_port(port, pal_port_speed_t.BF_SPEED_25G, an, fec)
        
    def setup_40g_port(self, port, 
                        an = None, fec = pal_fec_type_t.BF_FEC_TYP_NONE):
        self.setup_port(port, pal_port_speed_t.BF_SPEED_40G, an, fec)

    def setup_50g_port(self, port, 
                        an = None, fec = pal_fec_type_t.BF_FEC_TYP_NONE):
        self.setup_port(port, pal_port_speed_t.BF_SPEED_50G, an, fec)

    def setup_100g_port(self, port, 
                        an = None, fec = pal_fec_type_t.BF_FEC_TYP_NONE):
        self.setup_port(port, pal_port_speed_t.BF_SPEED_100G, an, fec)

    def remove_port(self, port):
        if isinstance(port, str):
            port = g_port_dict[port]
        self.pal_client.pal_port_del(self.dev, port)

    def set_port_mtu(self, port, mtu):
        if isinstance(port, str):
            port = g_port_dict[port]
        self.pal_client.pal_port_mtu_set(self.dev, port, mtu, mtu)

    def get_port_ops(self, port):
        if isinstance(port, int) == False:
            port = g_port_dict[port]
        return self.pal_client.pal_port_oper_status_get(self.dev, port)
    
    def clean_up_all_ports(self):
        self.pal_client.pal_port_del_all(self.dev)

    def clean_up_port(self, port):
        if isinstance(port, int) == False:
            port = g_port_dict[port]
        self.pal_client.pal_port_del(self.dev, port)

    def add_mirror_session(self, mir_id, dst_port, pkt_len = 1024):
        if isinstance(dst_port, str):
            dst_port = g_port_dict[dst_port]
        info = mirror_session(MirrorType_e.PD_MIRROR_TYPE_NORM,
                              Direction_e.PD_DIR_BOTH,
                              mir_id, dst_port,
                              True, max_pkt_len=pkt_len)
        self.mir_client.mirror_session_create(self.sess_hdl, 
                                          self.dev_tgt, info)
        self.mir_client.mirror_session_enable(self.sess_hdl, 
                                              Direction_e.PD_DIR_BOTH, 
                                            self.dev_tgt, mir_id)

    def del_mirror_session(self, mir_id):
        self.mir_client.mirror_session_delete(self.sess_hdl, self.dev_tgt, mir_id)

    def set_negative_mirror(self):
        all_dev_port = fp_ports_25G.values() + fp_ports_100G.values()
        for dev_port in all_dev_port:
            self.tm_client.tm_enable_q_tail_drop(g_device, dev_port, 0)

        self.tm_client.tm_set_negative_mirror_dest(g_device, 0, 40, 7)
        self.tm_client.tm_set_negative_mirror_dest(g_device, 1, 188, 7)

    def get_queue_drop_count(self, pipe, port, queue):
        return self.tm_client.tm_get_q_drop(g_device, pipe, port, queue)

    def get_queue_usage(self, pipe, port, queue):
        return self.tm_client.tm_get_q_usage(g_device, pipe, port, queue)
    

    def config_ppg(self, port, poolid, gmin, base_limit, dyn_baf, 
                    hysteresis, skid_limit, lossless_en, icos):
        ppg_hdl = self.tm_client.tm_allocate_ppg(g_device, port)
        self.tm_client.tm_set_ppg_app_pool_usage(g_device, ppg_hdl, poolid,           \
                                                base_limit, dyn_baf, hysteresis)    

        self.tm_client.tm_set_ppg_guaranteed_min_limit(g_device, ppg_hdl, gmin)
        if lossless_en:
            self.tm_client.tm_enable_lossless_treatment(g_device, ppg_hdl)
            self.tm_client.tm_set_ppg_skid_limit(g_device, ppg_hdl, skid_limit)
        else:
            self.tm_client.tm_disable_lossless_treatment(g_device, ppg_hdl)

        icos_bmap = (1 << icos)
        self.tm_client.tm_set_ppg_icos_mapping(g_device, ppg_hdl, icos_bmap)

    def config_queue(self, port, qid, poolid, base, dyn_baf, 
                        hysteresis, gmin, priority, dwrr_weight, pfc_cos):
        self.tm_client.tm_set_q_app_pool_usage(g_device, port, qid, 
                                                poolid, base, dyn_baf, hysteresis)
        self.tm_client.tm_set_q_guaranteed_min_limit(g_device, port, qid, gmin)
        if priority is not None:
            self.tm_client.tm_set_q_sched_priority(g_device, port, qid, priority)

        if dwrr_weight is not None:
            self.tm_client.tm_set_q_dwrr_weight(g_device, port, qid, dwrr_weight)
        
        if pfc_cos is not None:
            self.tm_client.tm_set_q_pfc_cos_mapping(g_device, port, qid, pfc_cos)   
    
    def init_default_ppg_queues(self):
        max_port = 64
        if hw_type == "motara":
            max_pipe = 2
        else:
            max_pipe = 4
            
        for pipe_id in range(0, max_pipe):
            for port in range(0, max_port):
                dev_port = ((pipe_id << 7) | port)
                # print dev_port
                
                ppg = self.tm_client.tm_get_default_ppg(g_device, dev_port)
                self.tm_client.tm_set_ppg_guaranteed_min_limit(g_device, ppg, 0)

                for queue_id in range(0, 8):
                    self.tm_client.tm_set_q_guaranteed_min_limit(g_device, dev_port, queue_id, 0)
                    
    def init_negative_mirror(self):
        self.tm_client.tm_set_negative_mirror_pool_size(g_device, 160)

    def init_uc_mc_cut_through(self):
        self.tm_client.tm_set_uc_cut_through_pool_size(g_device, 0)
        self.tm_client.tm_set_mc_cut_through_pool_size(g_device, 0)
            
    def set_buffer_pool_size(self, poolid, size_cells):
        self.tm_client.tm_set_app_pool_size(g_device, poolid, size_cells)

    def set_buffer_pool_skid_size(self, poolid, size_cells):
        self.tm_client.tm_set_skid_pool_size(g_device, size_cells)
        
    def create_buffer(self):        
        self.initDefaultPpgQueues()
        self.initNegativeMirror()

        # set UC/MC cut-through threshold to zero.
        self.initUcMcCutThrough()

        # configure zero size for unused pools.
        self.setBufferPoolSize(BF_TM_IG_APP_POOL_2, 0)
        self.setBufferPoolSize(BF_TM_IG_APP_POOL_3, 0)

        # Set 2 egress pools, set zero pool size for unused pools
        # Pool3 has a default pool for multicast. don't touch that pool.
        self.setBufferPoolSize(BF_TM_EG_APP_POOL_2, 0)
        

        self.setBufferPoolSize(ingress_lossless_pool_id, ingress_lossless_pool_size)
        self.setBufferPoolSize(ingress_lossy_pool_id, ingress_lossy_pool_size)
        
        self.setBufferPoolSize(egress_lossless_pool_id, egress_lossless_pool_size)
        self.setBufferPoolSize(egress_lossy_pool_id, egress_lossy_pool_size)

        self.setBufferPoolSkidSize(ingress_lossless_pool_id, skid_pool_size)

    def create_ppg(self):        
        all_dev_port = fp_ports_25G.values() + fp_ports_100G.values()
            
        for dev_port in all_dev_port:
            self.ppgConfig(dev_port, ingress_lossless_pool_id, ppg_gmin, ppg_base, \
                           ppg_lossless_baf, ppg_hysteresis, ppg_skid, 1, rdma_icos)
            
            self.ppgConfig(dev_port, ingress_lossy_pool_id, ppg_gmin, ppg_base, \
                           ppg_lossy_baf, ppg_hysteresis, 0, 0, cnp_icos)
            
            self.ppgConfig(dev_port, ingress_lossy_pool_id, ppg_gmin, ppg_base, \
                           ppg_lossy_baf, ppg_hysteresis, 0, 0, lossy_icos)

    def create_queue(self):        
        all_dev_port = fp_ports_25G.values() + fp_ports_100G.values()
        
        for dev_port in all_dev_port:           
            for  q in queue_map:
                if q == rdma_qid:
                    self.queueConfig(dev_port, q, egress_lossless_pool_id, \
                                queue_base, queue_lossless_baf, queue_hysteresis, \
                                queue_gmin, queue_priority[q], queue_weight[q], pfc_cos)
                elif q == cnp_qid: 
                    self.queueConfig(dev_port, q, egress_lossy_pool_id, \
                                    queue_base, queue_lossy_baf, queue_hysteresis, \
                                    queue_gmin, queue_priority[q], queue_weight[q],  None)
                else:
                    self.queueConfig(dev_port, q, egress_lossy_pool_id, \
                                queue_base, queue_lossy_baf, queue_hysteresis, \
                                queue_gmin, queue_priority[q], queue_weight[q], None)
    
    def insert_packet(self, pkt, port):
        pass