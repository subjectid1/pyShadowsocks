#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
import socket
import unittest

import constants
from protocol.shadowsocks.header import ShadowsocksPacketHeader


class HeaderTest(unittest.TestCase):
    def test_fields(self):
        header = ShadowsocksPacketHeader()
        header.port = 999
        header.addr_type = 1
        header.addr = '192.168.18.1'

        self.assertEqual(header.port, 999)
        self.assertEqual(header.addr_type, 1)
        self.assertEqual(header.addr, '192.168.18.1')

        # specified fields that do not assigned will return None instead of rasing KeyError
        self.assertIsNone(header.sha1_hmac)

        with self.assertRaises(KeyError):
            header.not_exist = 9

    def test_equal(self):
        header1 = ShadowsocksPacketHeader(port=80, addr_type=constants.SOCKS5_ADDRTYPE_HOST, addr='www.google.com')
        header2 = ShadowsocksPacketHeader(port=80, addr_type=constants.SOCKS5_ADDRTYPE_HOST, addr='www.google.com')
        self.assertEqual(header1, header2)

    def test_to_bytes_and_from_bytes(self):
        header1 = ShadowsocksPacketHeader(port=80, addr_type=constants.SOCKS5_ADDRTYPE_HOST, addr='www.google.com')
        bytes1 = b'\x03\x0ewww.google.com\x00\x50'
        self.assertEqual(header1.to_bytes(), bytes1)
        header1_new = ShadowsocksPacketHeader()
        header1_new.from_bytes(bytes1)
        self.assertEqual(header1_new, header1)

        header2 = ShadowsocksPacketHeader(port=53, addr_type=constants.SOCKS5_ADDRTYPE_IPV4, addr='8.8.8.8')
        bytes2 = b'\x01\x08\x08\x08\x08\x00\x35'
        self.assertEqual(header2.to_bytes(), bytes2)
        header2_new = ShadowsocksPacketHeader()
        header2_new.from_bytes(bytes2)
        self.assertEqual(header2_new, header2)

        header3 = ShadowsocksPacketHeader(port=80, addr_type=constants.SOCKS5_ADDRTYPE_IPV6,
                                          addr='2404:6800:4005:805::1011')
        bytes3 = b'\x04$\x04h\x00@\x05\x08\x05\x00\x00\x00\x00\x00\x00\x10\x11\x00\x50'
        self.assertEqual(header3.to_bytes(), bytes3)
        header3_new = ShadowsocksPacketHeader()
        header3_new.from_bytes(bytes3)
        self.assertEqual(header3_new, header3)

    def test_inet_pton(self):
        ipv4 = '8.8.4.4'
        b = socket.inet_pton(socket.AF_INET, ipv4)
        self.assertEqual(socket.inet_ntop(socket.AF_INET, b), ipv4)
        ipv6 = '2404:6800:4005:805::1011'
        b = socket.inet_pton(socket.AF_INET6, ipv6)
        self.assertEqual(socket.inet_ntop(socket.AF_INET6, b), ipv6)
