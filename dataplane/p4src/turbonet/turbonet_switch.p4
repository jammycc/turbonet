#ifndef _TURBONET_SWITCH_P4_
#define _TURBONET_SWITCH_P4_

#include "modules/route/ipv4.p4"

control eswitch_ingress {
    ipv4_forward();
}

#endif /*  */