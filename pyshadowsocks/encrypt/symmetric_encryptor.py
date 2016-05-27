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
        self.cipher_method = cipher
        self.encrypt_context = symmetric.create_context(self.cipher_method, key, iv, encrypt=True)
        self.decrypt_context = symmetric.create_context(self.cipher_method, key, iv, encrypt=False)

    def _check_key_iv_length(self, cipher, key, iv):
        from encrypt import SymmetricEncryptionsKeyAndIVLength
        KEY_LENGTH, IV_LENGTH = SymmetricEncryptionsKeyAndIVLength[cipher]
        if len(key) != KEY_LENGTH or len(iv) != IV_LENGTH:
            raise KeyError('invalid key or iv length')

    def encode(self, data: bytes, end=True):
        if len(data) == 0:
            return b''

        d = symmetric.update(self.encrypt_context, data)
        if end:
            d = d + symmetric.final(self.encrypt_context)
        return d

    def decode(self, data: bytes, end=True):
        if len(data) == 0:
            return b''

        d = symmetric.update(self.decrypt_context, data)
        if end:
            d = d + symmetric.final(self.decrypt_context)
        return d

    def __del__(self):
        symmetric.destrop_context(self.encrypt_context)
        symmetric.destrop_context(self.decrypt_context)
