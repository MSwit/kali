#!/usr/bin/env python3

import scapy.all as scapy
import socket


def scan(ip):

    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")

    arp_request_broadcast = broadcast/arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=3, verbose=True, iface="wlan0")[0]
    
    clients_list = []
    for element in answered_list:
        client_dict = {"ip": element[1].psrc, "mac": element[1].hwsrc}
        clients_list.append(client_dict)
    return clients_list


def print_result(results_list):

    print("IP\t\t\tMAC Address\n-------------------------------------------")
    for client in results_list:
        try:
            details = str(socket.gethostbyaddr(client['ip']))
        except:
            details = "error getting details"
        print(client['ip'] + "\t\t" + client['mac'] + "\t\t" + details)


scan_result = scan("192.168.178.0/24")
print_result(scan_result)
