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
            args='remote --listen_port 9999 shadowsocks --password 123456 --cipher_method aes-256-cfb'.split(' '))
        self.assertEqual(ns.protocol_mode, constants.ARG_PROTOCOL_SHADOWSOCKS)
        self.assertEqual(ns.server_mode, constants.ARG_REMOTE_SERVER)
        self.assertEqual(ns.listen_port, 9999)
        self.assertEqual(ns.password, '123456')
        self.assertEqual(ns.cipher_method, 'aes-256-cfb')
        self.assertEqual(ns.ota_enabled, False)

        ns = parse_args_new(
            args='local --remote_host 54.32.22.33 --remote_port 9999 --listen_port 1080 shadowsocks --password 123456 --cipher_method aes-256-cfb'.split(
                ' '))
        self.assertEqual(ns.protocol_mode, constants.ARG_PROTOCOL_SHADOWSOCKS)
        self.assertEqual(ns.server_mode, constants.ARG_LOCAL_SERVER)
        self.assertEqual(ns.remote_host, '54.32.22.33')
        self.assertEqual(ns.remote_port, 9999)
        self.assertEqual(ns.listen_port, 1080)
        self.assertEqual(ns.password, '123456')
        self.assertEqual(ns.cipher_method, 'aes-256-cfb')
        self.assertEqual(ns.ota_enabled, False)
