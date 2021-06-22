#ifndef _TURBONET_P4_
#define _TURBONET_P4_

#include "turbonet_metadata.p4"
#include "turbonet_link.p4"
#include "turbonet_switch.p4"

control turbonet_ingress {
    elink_input();
    eswitch_ingress();
    elink_output();
}

#endif  /* _TURBONET_P4_ */ 