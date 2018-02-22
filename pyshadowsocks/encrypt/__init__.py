#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: 
# 
# Info:
#
#

from encrypt.symmetric_encryptor import SymmetricEncryptor
from .oscrypto.openssl.symmetric import get_key_and_iv_length

AES_128_CFB = 'aes-128-cfb'
AES_256_CFB = 'aes-256-cfb'

SymmetricEncryptions = {
    AES_128_CFB: SymmetricEncryptor,
    AES_256_CFB: SymmetricEncryptor,
}

SymmetricEncryptionsKeyAndIVLength = {AES_128_CFB: (16, 16), AES_256_CFB: (32, 16)}
