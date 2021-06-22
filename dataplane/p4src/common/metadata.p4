/**
 * Authors:
 *     Yu Zhou, Tsinghua University, y-zhou16@mails.tsinghua.edu.cn
 * File Description:
 *     The flow metadata.
 */

#ifndef _FLOW_P4_
#define _FLOW_P4_

/* Common Metadata */
header_type flow_md_t {
    fields {
        src_ip      : 32;
        dst_ip      : 32;
        src_port    : 16;
        dst_port    : 16;
        protocol    : 8;
    }
}
metadata flow_md_t flow_md;

#endif /* _FLOW_P4_ */