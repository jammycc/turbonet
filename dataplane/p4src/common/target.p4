/**
 * Authors:
 *     Yu Zhou, Tsinghua University, y-zhou16@mails.tsinghua.edu.cn
 * File Description:
 *     The target-specific definition.
 */

#ifndef _TARGET_P4_
#define _TARGET_P4_

#include <tofino/intrinsic_metadata.p4>
#include <tofino/stateful_alu_blackbox.p4>
#include <tofino/constants.p4>
#include <tofino/primitives.p4>

#define _ingress_qid_   ig_intr_md_for_tm.qid
#define _egress_qid_    eg_intr_md.egress_qid
#define _queue_len_     eg_intr_md.deq_qdepth
#define _deq_len_       eg_intr_md.deq_qdepth
#define _enq_len_       eg_intr_md.enq_qdepth
#define _parser_cntr_   ig_prsr_ctrl.parser_counter
#define _ingress_port_  ig_intr_md.ingress_port
#define _egress_spec_   ig_intr_md_for_tm.ucast_egress_port
#define _egress_port_   eg_intr_md.egress_port
#define _deq_delta_     eg_intr_md.deq_timedelta
#define _enq_ts_        eg_intr_md.enq_tstamp
#define _ingress_ts_    ig_intr_md.ingress_mac_tstamp
#define _egress_ts_     eg_intr_md_from_parser_aux.egress_global_tstamp
#define _pkt_len_       eg_intr_md.pkt_length

#endif /* _TARGET_P4_ */