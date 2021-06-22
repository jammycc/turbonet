/**
 * Authors:
 *     Yu Zhou, Tsinghua University, y-zhou16@mails.tsinghua.edu.cn
 * File Description:
 *     Forwarding module.
 */

#ifndef _IPV4_FORWARD_P4_
#define _IPV4_FORWARD_P4_

action set_egress_port(port) {
    modify_field(turbonet_ingress_md.egress_eport_id, port);
}

table ipv4_forward {
    reads {
        turbonet_ingress_md.eswitch_id  : exact;
        // flow_md.dst_ip          : exact;
        flow_md.dst_ip          : lpm;
    }
    actions {
        set_egress_port;
    }
    size : 1024;
}

control ipv4_forward {
    apply(ipv4_forward);
}

#endif /* _FORWARD_P4_ */