#ifndef _TURBONET_LINK_P4_
#define _TURBONET_LINK_P4_

/*
 * loopback --> elink_ingress --> (eswitch_id, ingress_eport_id) --> eswitch_ingress 
 */
action get_eswitch(eswitch_id, eport_id) {
    modify_field(turbonet_ingress_md.eswitch_id, eswitch_id);
    modify_field(turbonet_ingress_md.ingress_eport_id, eport_id);
}
action add_ehdr(eswitch_id, eport_id) {
    add_header(ehdr);
    get_eswitch(eswitch_id, eport_id);
}

table get_eswitch_from_elink {
    reads {
        // turbonet_ingress_md.prev_eswitch_id  : exact;
        // turbonet_ingress_md.prev_eport_id    : exact;
        ehdr.eswitch_id :   exact;
        ehdr.eport_id   :   exact;
    }
    actions {
        get_eswitch;
    }
    size : 512;
}

table get_eswitch_from_plink {
    reads {
        _ingress_port_     : exact;
    }
    actions {
        add_ehdr;
    }
    size : 512;
}

control elink_input {
    if (valid(ehdr)) {
        apply(get_eswitch_from_elink);
    } else {
        apply(get_eswitch_from_plink);
    }
}

action get_next_elink(port) {
    modify_field(ehdr.eswitch_id, turbonet_ingress_md.eswitch_id);
    modify_field(ehdr.eport_id, turbonet_ingress_md.egress_eport_id);
    modify_field(_egress_spec_, port);
}
action remove_ehdr(port) {
    remove_header(ehdr);
    modify_field(_egress_spec_, port);
}
table get_elink {
    reads {
        turbonet_ingress_md.eswitch_id      : exact;
        turbonet_ingress_md.egress_eport_id : exact;
    }
    actions {
        get_next_elink;
        remove_ehdr;
    }
    size : 512;
}
control elink_output {
    apply(get_elink);
}

#endif /* TURBONET_LINK_P4_ */