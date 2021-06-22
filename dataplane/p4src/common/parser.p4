/**
 * Authors:
 *     
 * File Description:
 *     The parser definition.
 */

#ifndef _PARSER_P4_
#define _PARSER_P4_

parser start {
    return select(current(0, 4)) {
        0       : parse_ehdr;
        default : parse_ethernet;
    }
}

parser parse_ehdr {
    extract(ehdr);
    return parse_ethernet;
}

parser parse_ethernet {
    extract(ethernet);
    return select(latest.ether_type) {
        ETHERTYPE_IPV4   : parse_ipv4;  
        default: ingress;
    }
}

parser parse_arp {
    extract(arp);
    set_metadata(flow_md.dst_ip, arp.dst_proto_addr);
    return ingress;
}

parser parse_ipv4 {
    extract(ipv4);
    
    /*
    set_metadata(global_field_set.ipv4_src_ip, ipv4.src_ip);
    set_metadata(global_field_set.ipv4_dst_ip, ipv4.dst_ip);
    set_metadata(global_field_set.ipv4_proto, ipv4.proto);
    */
    set_metadata(flow_md.dst_ip, ipv4.dst_ip);   
    set_metadata(flow_md.src_ip, ipv4.src_ip);    
    set_metadata(flow_md.protocol, ipv4.protocol);
    
    return select(latest.protocol) {
        IP_PROTOCOLS_TCP : parse_tcp;
        IP_PROTOCOLS_UDP : parse_udp;
        default: ingress;
    }
}

parser parse_tcp {
    extract(tcp);

    /*
    set_metadata(global_field_set.src_port, tcp.src_port);
    set_metadata(global_field_set.dst_port, tcp.dst_port);
    set_metadata(global_field_set.tcp_flag, tcp.ctrl);
    */
    set_metadata(flow_md.dst_port, tcp.dst_port);   
    set_metadata(flow_md.src_port, tcp.src_port);    
    
    return ingress;
}

parser parse_udp {
    extract(udp);
    /*
    set_metadata(global_field_set.src_port, udp.src_port);
    set_metadata(global_field_set.dst_port, udp.dst_port);
    */
    set_metadata(flow_md.dst_port, udp.dst_port);   
    set_metadata(flow_md.src_port, udp.src_port);  

    return ingress;
}

#endif /* _PARSER_P4_ */