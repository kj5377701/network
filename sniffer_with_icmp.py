import socket
import os
import struct
from ctypes import *

host = '192.168.136.130'


class IP(Structure):
    _fields_ = [
        ('ihl', c_uint8, 4),
        ('version', c_uint8, 4),
        ('tos', c_uint8),
        ('len', c_uint16),
        ('id', c_uint16),
        ('offset', c_uint16),
        ('ttl', c_uint8),
        ('protocol_num', c_uint8),
        ('sum', c_uint16),
        ('src', c_uint32),
        ('dst', c_uint32)
    ]

    def __new__(cls, socket_buffer=None):
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        self.protocol_map = {1: 'ICMP', 6: 'TCP', 17: 'UDP'}
        self.src_address = socket.inet_ntoa(struct.pack('<L', self.src))
        self.dst_address = socket.inet_ntoa(struct.pack('<L', self.dst))
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)


class ICMP(Structure):
    _fields_ = [
        ('type', c_uint8),
        ('code', c_uint8),
        ('checksum', c_uint16),
        ('unused', c_uint16),
        ('next_hop_mtu', c_uint16)
    ]

    def __new__(cls, socket_buffer):
        return cls.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer):
        pass


if os.name == 'nt':
    socket_protocol = socket.IPPROTO_IP
else:
    socket_protocol = socket.IPPROTO_ICMP
sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
sniffer.bind((host, 0))
sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

if os.name == 'nt':
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

try:
    while 1:
        raw_buffer = sniffer.recvfrom(65565)[0]
        ip_header = IP(raw_buffer[0:20])

        print('protocol: %s %s -> %s' % (ip_header.protocol, ip_header.src_address, ip_header.dst_address))
        if ip_header.protocol == 'ICMP':
            offset = ip_header.ihi * 4
            buf = raw_buffer[offset:offset + sizeof(ICMP)]
            icmp_header = ICMP(buf)
            print('type: %d Code: %d' % (icmp_header.type, icmp_header.code))
except KeyboardInterrupt:
    if os.name == 'nt':
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
