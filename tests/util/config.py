#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
import unittest

from util.config import get_config


class ConfigTest(unittest.TestCase):
    def test_get_config(self):
        config = get_config()
        section = config['shadowsocks']
        self.assertEqual(section.get('password'), '123456')

