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
from util import what_type_of_the_address


class AddressTest(unittest.TestCase):
    def test_what_type_of_the_address(self):
        type1 = what_type_of_the_address('www.google.com')
        self.assertEqual(type1, constants.SOCKS5_ADDRTYPE_HOST)

        type2 = what_type_of_the_address('192.168.1.1')
        self.assertEqual(type2, constants.SOCKS5_ADDRTYPE_IPV4)

        type3 = what_type_of_the_address('2404:6800:4005:805::1011')
        self.assertEqual(type3, constants.SOCKS5_ADDRTYPE_IPV6)

