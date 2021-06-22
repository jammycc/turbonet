
#include "common/const.p4"
#include "common/headers.p4"
#include "common/metadata.p4"
#include "common/parser.p4"
#include "common/target.p4"

#include "turbonet/turbonet.p4"

control ingress {
    turbonet_ingress();
}

control egress {

}