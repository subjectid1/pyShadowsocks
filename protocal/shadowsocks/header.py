#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
import socket

import constants
import struct
from packet.packet_header import PacketHeader


class Socks5AddrHeader(PacketHeader):
    ValidFields = ['addr_type', 'addr', 'port']

    def is_valid(self):
        valid = True
        if not self.addr_type in [constants.SOCKS5_ADDRTYPE_IPV4, constants.SOCKS5_ADDRTYPE_IPV6,
                                  constants.SOCKS5_ADDRTYPE_HOST]:
            valid = False
        elif not isinstance(self.port, int):
            valid = False

        return valid

    def to_bytes(self):
        """pack header to bytes like: | Addr type(0x01) | Addr | Port | """

        if not self.is_valid():
            raise AttributeError

        addr_bytes = self._pack_addr_bytes_from(self.addr_type, self.addr)
        port_bytes = struct.pack('>H', self.port)

        return addr_bytes + port_bytes

    def from_bytes(self, data):
        """
        raise ValueError when no inough data income,
        raise IOError when invalid structure
        return header length when successfully unpack data
        """
        addr_length, addrtype, dest_addr = self._unpack_addr_from(data)
        if len(data[addr_length:]) < 2:
            raise ValueError()

        self.port, = struct.unpack_from('>H', data, addr_length)
        self.addr_type = addrtype
        self.addr = dest_addr
        return addr_length + struct.calcsize('>H')

    def _pack_addr_bytes_from(self, addr_type, addr):
        addr_bytes = None
        if addr_type in [constants.SOCKS5_ADDRTYPE_IPV4, constants.SOCKS5_ADDRTYPE_IPV6]:

            addr_bytes = socket.inet_pton({constants.SOCKS5_ADDRTYPE_IPV4: socket.AF_INET,
                                           constants.SOCKS5_ADDRTYPE_IPV6: socket.AF_INET6}[addr_type],
                                          addr)

        elif addr_type == constants.SOCKS5_ADDRTYPE_HOST:
            if len(addr) > 255:
                addr = addr[:255]
            addr_bytes = chr(len(addr)) + addr
            addr_bytes = addr_bytes.encode('utf-8')

        addr_bytes = chr(addr_type).encode('utf-8') + addr_bytes
        return addr_bytes

    def _unpack_addr_from(self, data):
        addr_type = ord(data[:1])
        dest_addr = None
        addr_data = data[1:]
        addr_length = 0

        exception_when_no_enough_data = ValueError("no enough data to unpack")

        if addr_type & constants.ADDRTYPE_MASK == constants.SOCKS5_ADDRTYPE_IPV4:
            if len(addr_data) >= 4:
                dest_addr = socket.inet_ntop(socket.AF_INET, addr_data[:4])
                addr_length = 5
            else:
                raise exception_when_no_enough_data

        elif addr_type & constants.ADDRTYPE_MASK == constants.SOCKS5_ADDRTYPE_HOST:
            if len(addr_data) > 2:
                field_len = ord(addr_data[:1])
                remain_data = addr_data[1:]

                if len(remain_data) >= field_len:
                    dest_addr = (remain_data[:field_len]).decode('utf-8')
                    addr_length = 2 + field_len
                else:
                    raise exception_when_no_enough_data
            else:
                raise exception_when_no_enough_data
        elif addr_type & constants.ADDRTYPE_MASK == constants.SOCKS5_ADDRTYPE_IPV6:
            if len(addr_data) >= 16:
                dest_addr = socket.inet_ntop(socket.AF_INET6, addr_data[:16])
                addr_length = 17
            else:
                raise exception_when_no_enough_data
        else:
            raise IOError('unsupported addrtype %d, maybe wrong password or '
                          'encryption method' % addr_type)

        return addr_length, addr_type, dest_addr


class ShadowsocksPacketHeader(Socks5AddrHeader):
    ValidFields = ['addr_type', 'addr', 'port', 'sha1_hmac']

    def to_bytes(self):
        data = super(ShadowsocksPacketHeader, self).to_bytes()
        sha1_hmac = self.sha1_hmac or b''
        return data + sha1_hmac
