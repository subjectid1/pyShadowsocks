#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: 
# 
# Info:
#
#

import unittest
import encrypt
import os


class AES256CFBTest(unittest.TestCase):
    def test(self):
        CryptoCls = encrypt.SymmetricEncryptions[encrypt.CRYPTO_AES_256_CFB]

        crypto = CryptoCls(os.urandom(CryptoCls.KEY_LENGTH),
                           os.urandom(CryptoCls.IV_LENGTH))

        text1 = b"a secret message"
        ct = crypto.encode(text1, end=True)
        text2 = crypto.decode(ct, end=True)
        self.assertEqual(text1, text2)

        text1 = b''
        ct = crypto.encode(text1, end=True)
        text2 = crypto.decode(ct, end=True)
        self.assertEqual(text1, text2)

