#!/usr/bin/env python3
import scapy.all as scapy
interface = 'wlan0'

# Packet 'p' below is incomplete, but it doesn't matter
p = scapy.Ether(src=scapy.get_if_hwaddr(interface)) / scapy.IP(dst='192.168.178.1',
                                                               src='192.168.178.23') / scapy.UDP(dport=53, chksum=0)
scapy.sendp(p, iface=interface, verbose=True)
