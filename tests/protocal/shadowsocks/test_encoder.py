#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
import unittest
import encrypt
import os
import random
from protocal.shadowsocks.encoder import EVP_BytesToKey, ShadowsocksEncryptionWrapperEncoder


class ShadowsocksCipherTest(unittest.TestCase):
    def test_EVP_BytesToKey(self):
        expected_res = (b"\xe1\n\xdc9I\xbaY\xab\xbeV\xe0W\xf2\x0f\x88>e\xb4\xad'\x0b;\x98\t\x8d%j\xb3/[\x8f\xba",
                        b'\x94\x90\xb8x\x0b\x19\x86\xd7\x19`7\xe87\xc0\x9f\x16')

        res = EVP_BytesToKey(b'123456', 32, 16)
        self.assertEqual(expected_res, res)

    def test_ShadowsocksEncryptionWrapperEncoder(self):
        encoder = ShadowsocksEncryptionWrapperEncoder(
            encrypt_method=encrypt.CRYPTO_AES_256_CFB,
            encript_mode=True,
            password=b'123456'
        )

        decoder = ShadowsocksEncryptionWrapperEncoder(
            encrypt_method=encrypt.CRYPTO_AES_256_CFB,
            encript_mode=False,
            password=b'123456'
        )

        raw_data = os.urandom(random.randint(20, 30))

        encoded_data = encoder.encode(raw_data, end=True)
        decoded_data = decoder.decode(encoded_data, end=True)
        self.assertEqual(raw_data, decoded_data)
