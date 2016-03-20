#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
from encrypt.base.data_encoder import DataEncoder


class SymmetricEncryptor(DataEncoder):

    KEY_LENGTH = NotImplementedError()
    IV_LENGTH = NotImplementedError()

    def __init__(self, key:bytes=None, iv:bytes=None):
        self._check_key_iv_length(key, iv)

        self.key = key
        self.iv = iv

    def _check_key_iv_length(self, key, iv):
        if len(key) != self.KEY_LENGTH or len(iv) != self.IV_LENGTH:
            raise KeyError('invalid key or iv length')