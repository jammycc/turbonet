#ifndef _TURBONET_METADATA_P4_
#define _TURBONET_METADATA_P4_

header_type turbonet_ingress_md_t {
    fields {
        prev_eswitch_id     : 16;
        prev_eport_id       : 16;

        eswitch_id          : 16;
        ingress_eport_id    : 16;
        egress_eport_id     : 16;
    }
}
metadata turbonet_ingress_md_t turbonet_ingress_md;


#endif /* _TURBONET_METADATA_P4 */