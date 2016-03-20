#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info: https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption/
#
#
from cryptography.exceptions import AlreadyFinalized
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from encrypt.base.symmetric_encryptor import SymmetricEncryptor


class AES_256_CFB(SymmetricEncryptor):
    KEY_LENGTH = 32
    IV_LENGTH = 16

    def __init__(self, key=None, iv=None):
        super(AES_256_CFB, self).__init__(key, iv)

        # key = os.urandom(32)
        # iv = os.urandom(16)
        backend = default_backend()
        self.cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=backend)
        self.encryptor = self.cipher.encryptor()
        self.decryptor = self.cipher.decryptor()

    def encode(self, text: bytes, end=False):
        if len(text) == 0:
            return b''

        encoded_data = self.encryptor.update(text)
        if end:
            try:
                encoded_data_end = self.encryptor.finalize()
                encoded_data += encoded_data_end
            except AlreadyFinalized:
                pass

        return encoded_data

    def decode(self, cipher_text: bytes, end=False):
        if len(cipher_text) == 0:
            return b''

        encoded_data = self.decryptor.update(cipher_text)
        if end:
            try:
                encoded_data_end = self.decryptor.finalize()
                encoded_data += encoded_data_end
            except AlreadyFinalized:
                pass

        return encoded_data
