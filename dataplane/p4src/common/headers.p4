#ifndef _HEADERS_P4_
#define _HEADERS_P4_

header_type emulator_t {
    fields {
        pad             : 4;
        be_delayed      : 4;
        remained_cycles : 8;
        eswitch_id      : 16;
        eport_id        : 16;
    }
}
header emulator_t ehdr;

header_type ethernet_t {
    fields {
        dst_addr    : 48;
        src_addr    : 48;
        ether_type  : 16;
    }
}
header ethernet_t  ethernet;

header_type ipv4_t {
    fields {
        version         : 4;
        ihl             : 4;
        diffserv        : 8;
        total_len       : 16;
        identification  : 16;
        flags           : 3;
        frag_offset     : 13;
        ttl             : 8;
        protocol        : 8;
        checksum        : 16;
        src_ip          : 32;
        dst_ip          : 32;
    }
}
header ipv4_t ipv4;

header_type tcp_t {
    fields {
        src_port        : 16;
        dst_port        : 16;
        seq_no          : 32;
        ack_no          : 32;
        data_offset     : 4;
        res             : 3;
        ecn             : 3;
        ctrl            : 6;
        window          : 16;
        checksum        : 16;
        urgent_ptr      : 16;
    }
}
header tcp_t tcp;

header_type udp_t {
    fields {
        src_port        : 16;
        dst_port        : 16;
        hdr_length      : 16;
        checksum        : 16;
    }
}
header udp_t udp;

header_type arp_t {
    fields {
        hw_type         : 16;
        proto_type      : 16;
        hw_addr_len     : 8;
        proto_addr_len  : 8;
        opcode          : 16;
        src_hw_addr     : 48;
        src_proto_addr  : 32;
        dst_hw_addr     : 48;
        dst_proto_addr  : 32;
    }
}
header arp_t arp;


#endif /* _HEADERS_ */