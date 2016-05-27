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
from encrypt.symmetric_encryptor import SymmetricEncryptor


class SymmetricTests(unittest.TestCase):
    def test_all_method(self):
        for encrypt_method in SymmetricEncryptions:
            key_size, iv_size = SymmetricEncryptionsKeyAndIVLength[encrypt_method]

            key = os.urandom(key_size)
            iv = os.urandom(iv_size)
            data = b'This is data to encrypt'

            crypter = SymmetricEncryptor(encrypt_method, key, iv)
            ciphertext = crypter.encode(data, end=True)

            self.assertEqual(bytes, type(ciphertext))

            plaintext = crypter.decode(ciphertext, end=True)
            self.assertEqual(data, plaintext)

    def test_update_and_end(self):
        for encrypt_method in SymmetricEncryptions:
            key_size, iv_size = SymmetricEncryptionsKeyAndIVLength[encrypt_method]

            key = os.urandom(key_size)
            iv = os.urandom(iv_size)
            crypter1 = SymmetricEncryptor(encrypt_method, key, iv)
            crypter2 = SymmetricEncryptor(encrypt_method, key, iv)
            crypter3 = SymmetricEncryptor(encrypt_method, key, iv)

            data_trunks = []
            cipher_data_trunks = []
            for i in range(5, 10000, 1):
                data_trunk = os.urandom(i)
                data_trunks.append(data_trunk)
                cipher_data_trunks.append(crypter1.encode(data_trunk, end=True))

            ## 看看分次加密和一次加密是不是会有不一样的结果
            raw_data = b''.join(data_trunks)
            cipher_data = crypter2.encode(raw_data, end=True)

            cipher_data2 = b''.join(cipher_data_trunks)
            raw_data2 = crypter3.decode(cipher_data2, end=True)


            self.assertEqual(len(raw_data), len(raw_data2))
            self.assertEqual(raw_data, raw_data2)
            self.assertEqual(cipher_data, cipher_data2)
