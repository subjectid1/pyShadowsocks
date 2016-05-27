#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: 
# 
# Info:
#
#

from encrypt.oscrypto.openssl.symmetric import get_key_and_iv_length
from encrypt.symmetric_encryptor import SymmetricEncryptor

AES_128_CFB = 'aes-128-cfb'
AES_256_CFB = 'aes-256-cfb'

SymmetricEncryptions = {
    AES_128_CFB: SymmetricEncryptor,
    AES_256_CFB: SymmetricEncryptor,
}

SymmetricEncryptionsKeyAndIVLength = {enc: get_key_and_iv_length(enc) for enc in SymmetricEncryptions}
