#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info: asyncio  - Stream<https://docs.python.org/3/library/asyncio-stream.html#asyncio-tcp-echo-server-streams>
#                - Transport<https://docs.python.org/3/library/asyncio-protocol.html>
#

from protocol.COMMON.common_relay_protocal import CommonClientRelayProtocal
from protocol.shadowsocks.encoder import ShadowsocksEncryptionWrapperEncoder


class ShadowsocksClientRelayProtocol(CommonClientRelayProtocal):
    def create_encoder(self):
        return ShadowsocksEncryptionWrapperEncoder(
            encrypt_method=self.config.cipher_method,
            password=self.config.password,
            encript_mode=True)

    def create_decoder(self):
        return ShadowsocksEncryptionWrapperEncoder(
            encrypt_method=self.config.cipher_method,
            password=self.config.password,
            encript_mode=False)
