#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
from encrypt.data_encoder import DataEncoder
from encrypt.oscrypto.openssl import symmetric


class SymmetricEncryptor(DataEncoder):
    def __init__(self, cipher, key: bytes, iv: bytes = None):
        from encrypt import SymmetricEncryptions
        assert (cipher in SymmetricEncryptions)
        self._check_key_iv_length(cipher, key, iv)

        self.key = key
        self.iv = iv
        self.cipher = cipher

    def _check_key_iv_length(self, cipher, key, iv):
        from encrypt import SymmetricEncryptionsKeyAndIVLength
        KEY_LENGTH, IV_LENGTH = SymmetricEncryptionsKeyAndIVLength[cipher]
        if len(key) != KEY_LENGTH or len(iv) != IV_LENGTH:
            raise KeyError('invalid key or iv length')

    def encode(self, data: bytes, end=False):
        if len(data) == 0:
            return b''

        return symmetric.encrypt(self.cipher, self.key, self.iv, data)

    def decode(self, data: bytes, end=False):
        if len(data) == 0:
            return b''

        return symmetric.decrypt(self.cipher, self.key, self.iv, data)
