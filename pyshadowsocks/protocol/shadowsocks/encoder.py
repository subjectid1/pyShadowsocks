#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
import hashlib
import os

from encrypt import SymmetricEncryptions, SymmetricEncryptionsKeyAndIVLength
from encrypt.data_encoder import DataEncoder


def EVP_BytesToKey(password, key_len, iv_len):
    # equivalent to OpenSSL's EVP_BytesToKey() with count 1
    # so that we make the same key and iv as nodejs version

    m = []
    i = 0
    while len(b''.join(m)) < (key_len + iv_len):
        md5 = hashlib.md5()
        data = password
        if i > 0:
            data = m[i - 1] + password
        md5.update(data)
        m.append(md5.digest())
        i += 1
    ms = b''.join(m)
    key = ms[:key_len]
    iv = ms[key_len:key_len + iv_len]
    return key, iv


class ShadowsocksEncryptionWrapperEncoder(DataEncoder):
    def __init__(self, encrypt_method=None, password=None, encript_mode=True):
        cipherCls = SymmetricEncryptions[encrypt_method]
        if isinstance(password, str):
            password = password.encode('utf-8')

        key_size, iv_size = SymmetricEncryptionsKeyAndIVLength[encrypt_method]

        key, _ = EVP_BytesToKey(password, key_size, iv_size)
        iv = os.urandom(iv_size)

        self.key = key
        self.iv = None
        self.encoder = None
        self.encrypt_method = encrypt_method

        if encript_mode:
            self.iv = iv
            self.encoder = cipherCls(encrypt_method, key, iv)
            self.is_iv_sent = False
        else:
            self.iv_buf = b''
            self.iv_length = iv_size
            self.cipherCls = cipherCls

    def encode(self, data, end=False):
        if not self.is_iv_sent:
            self.is_iv_sent = True
            return self.iv + self.encoder.encode(data, end=end)
        else:
            return self.encoder.encode(data, end=end)

    def decode(self, data, end=False):
        if not self.encoder:
            expected_iv_length = self.iv_length - len(self.iv_buf)

            if len(data) < expected_iv_length:
                self.iv_buf += data[:len(data)]
                return b''
            else:
                iv = self.iv_buf + data[:expected_iv_length]
                data_left = data[expected_iv_length:]

                self.encoder = self.cipherCls(self.encrypt_method, self.key, iv)
                self.iv = iv
                return self.encoder.decode(data_left, end=end)

        else:
            return self.encoder.decode(data, end=end)
