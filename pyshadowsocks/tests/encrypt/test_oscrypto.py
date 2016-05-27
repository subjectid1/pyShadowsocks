#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
import unittest

import os
from encrypt import SymmetricEncryptions, SymmetricEncryptionsKeyAndIVLength
from encrypt.oscrypto.openssl import symmetric


class SymmetricTests(unittest.TestCase):
    def test_all_method(self):
        for encrypt_method in SymmetricEncryptions:
            key_size, iv_size = SymmetricEncryptionsKeyAndIVLength[encrypt_method]

            key = os.urandom(key_size)
            iv = os.urandom(iv_size)
            data = b'This is data to encrypt'

            ciphertext = symmetric.encrypt(encrypt_method, key, iv, data)
            self.assertNotEqual(data, ciphertext)
            self.assertEqual(bytes, type(ciphertext))

            plaintext = symmetric.decrypt(encrypt_method, key, iv, ciphertext)
            self.assertEqual(data, plaintext)

    def test_update_and_end(self):
        for encrypt_method in SymmetricEncryptions:
            key_size, iv_size = SymmetricEncryptionsKeyAndIVLength[encrypt_method]

            key = os.urandom(key_size)
            iv = os.urandom(iv_size)

            data_trunks = []
            cipher_data_trunks = []
            for i in range(5, 13, 3):
                data_trunk = b'A' * i  # os.urandom(i)
                data_trunks.append(data_trunk)
                cipher_data_trunks.append(symmetric.encrypt(encrypt_method, key, iv, data_trunk))

            raw_data = b''.join(data_trunks)
            cipher_data = b''.join(cipher_data_trunks)

            raw_data2 = symmetric.decrypt(encrypt_method, key, iv, cipher_data)
            cipher_data2 = symmetric.encrypt(encrypt_method, key, iv, raw_data)

            self.assertEqual(len(raw_data), len(raw_data2))
            # self.assertEqual(raw_data, raw_data2)
            self.assertEqual(cipher_data, cipher_data2)
