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
from util import parse_args_new


class ConfigTest(unittest.TestCase):
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
