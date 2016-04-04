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
        d = {
            'password': '123456',
            'protocol': 'shadowsocks',
            'cipher_method': 'aes-256-cfb'
        }
        args = []
        for k, v in d.items():
            args.extend(['--' + k, v])

        d2 = parse_args(args)
        for k, v in d.items():
            self.assertEqual(v, d2[k])
