#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
import unittest

from util.config import get_config, parse_args


class ConfigTest(unittest.TestCase):
    def test_get_config(self):
        config = get_config()
        section = config['shadowsocks']
        self.assertEqual(section.get('password'), '123456')

    def test_parse_args(self):
        args_s = '--listen_port 80 --protocol shadowsocks --password 123456 --cipher_method aes-256-cfb'

        d = parse_args(False, args_s.split(' '))
        self.assertEqual(d['listen_port'], 80)

        args_s = '--remote_host 192.168.1.1 --remote_port 80 --protocol shadowsocks --password 123456 --cipher_method aes-256-cfb'

        d = parse_args(True, args_s.split(' '))
        self.assertEqual(d['remote_port'], 80)
