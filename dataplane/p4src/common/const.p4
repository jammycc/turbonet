/*
 * Authors:
 *      Yu Zhou, y-zhou16@mails.tsinghua.edu.cn
 *      Jiamin Cao, 
 * Description:
 *      Const values and types
 */

#ifndef _CONST_P4_
#define _CONST_P4_

/* Ethernet Types */
#define ETHERTYPE_VLAN          0x8100
#define ETHERTYPE_QINQ          0x9100
#define ETHERTYPE_MPLS          0x8847
#define ETHERTYPE_IPV4          0x0800
#define ETHERTYPE_IPV6          0x86dd
#define ETHERTYPE_ARP           0x0806
#define ETHERTYPE_RARP          0x8035
#define ETHERTYPE_NSH           0x894f
#define ETHERTYPE_ETHERNET      0x6558
#define ETHERTYPE_ROCE          0x8915
#define ETHERTYPE_FCOE          0x8906
#define ETHERTYPE_TRILL         0x22f3
#define ETHERTYPE_VNTAG         0x8926
#define ETHERTYPE_LLDP          0x88cc
#define ETHERTYPE_LACP          0x8809
#define ETHERTYPE_PTP           0x88f7
#define ETHERTYPE_FIP           0x8914

#define ETHERTYPE_NEWTON        0x8FFF

/* IP Protocols */
#define IP_PROTOCOLS_ICMP              1
#define IP_PROTOCOLS_IGMP              2
#define IP_PROTOCOLS_IPV4              4
#define IP_PROTOCOLS_TCP               6
#define IP_PROTOCOLS_UDP               17
#define IP_PROTOCOLS_IPV6              41
#define IP_PROTOCOLS_SR                43
#define IP_PROTOCOLS_GRE               47
#define IP_PROTOCOLS_IPSEC_ESP         50
#define IP_PROTOCOLS_IPSEC_AH          51
#define IP_PROTOCOLS_ICMPV6            58
#define IP_PROTOCOLS_EIGRP             88
#define IP_PROTOCOLS_OSPF              89
#define IP_PROTOCOLS_ETHERIP           97
#define IP_PROTOCOLS_PIM               103
#define IP_PROTOCOLS_VRRP              112

#define ICMP_TYPE_ECHO_REPLY                0
#define ICMP_TYPE_ECHO_REQUEST              8

#endif /* _CONST_P4_ */