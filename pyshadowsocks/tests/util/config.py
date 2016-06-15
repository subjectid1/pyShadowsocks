#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
import unittest

import constants
from util.config import get_config, parse_args_new


class ConfigTest(unittest.TestCase):
    def test_get_config(self):
        config = get_config()
        section = config['shadowsocks']
        self.assertEqual(section.get('password'), '123456')

    def test_parse_args(self):
        ns = parse_args_new(
            args='shadowsocks --password 123456 --cipher_method aes-256-cfb remote --listen_port 8033'.split(' '))
        self.assertEqual(ns.protocol_mode, constants.ARG_PROTOCOL_SHADOWSOCKS)
        self.assertEqual(ns.server_mode, constants.ARG_REMOTE_SERVER)
        self.assertEqual(ns.listen_port, 8033)
        self.assertEqual(ns.password, '123456')
        self.assertEqual(ns.cipher_method, 'aes-256-cfb')
        self.assertEqual(ns.ota_enabled, False)

        ns = parse_args_new(
            args='shadowsocks --cipher_method aes-256-cfb --password 123456 local --socks_port 1080 --remote_host 54.32.22.33 --remote_port 8033'.split(
                ' '))
        self.assertEqual(ns.protocol_mode, constants.ARG_PROTOCOL_SHADOWSOCKS)
        self.assertEqual(ns.server_mode, constants.ARG_LOCAL_SERVER)
        self.assertEqual(ns.remote_host, '54.32.22.33')
        self.assertEqual(ns.remote_port, 8033)
        self.assertEqual(ns.socks_port, 1080)
        self.assertEqual(ns.pac_port, None)

        self.assertEqual(ns.password, '123456')
        self.assertEqual(ns.cipher_method, 'aes-256-cfb')
        self.assertEqual(ns.ota_enabled, False)

        ns = parse_args_new(
            args='socks5ssl --user root --password=123456 remote --listen_port 9004'.split(
                ' '))
        self.assertEqual(ns.protocol_mode, constants.ARG_PROTOCOL_SOCKS5OVERSSL)
        self.assertEqual(ns.server_mode, constants.ARG_REMOTE_SERVER)
        self.assertEqual(ns.listen_port, 9004)
        self.assertEqual(ns.password, '123456')
        self.assertEqual(ns.user, 'root')

        # ss.py socks5ssl local --remote_host 127.0.0.1 --remote_port 9004 --socks_port 10010
        ns = parse_args_new(
            args='socks5ssl --user root --password=123456 local --remote_host 127.0.0.1 --remote_port 9004 --socks_port 10010'.split(
                ' '))
        self.assertEqual(ns.protocol_mode, constants.ARG_PROTOCOL_SOCKS5OVERSSL)
        self.assertEqual(ns.server_mode, constants.ARG_LOCAL_SERVER)
        self.assertEqual(ns.remote_host, '127.0.0.1')
        self.assertEqual(ns.remote_port, 9004)
        self.assertEqual(ns.socks_port, 10010)
        self.assertEqual(ns.pac_port, None)
        self.assertEqual(ns.password, '123456')
        self.assertEqual(ns.user, 'root')
