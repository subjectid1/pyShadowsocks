#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info: asyncio  - Stream<https://docs.python.org/3/library/asyncio-stream.html#asyncio-tcp-echo-server-streams>
#                - Transport<https://docs.python.org/3/library/asyncio-protocol.html>
#

import config
from packet.stream_packer import StreamPacker
from protocal.common_relay_protocal import CommonClientRelayProtocal
from protocal.shadowsocks.encoder import ShadowsocksEncryptionWrapperEncoder


class ShadowsocksClientRelayProtocol(CommonClientRelayProtocal):
    def create_packer(self):
        return StreamPacker(
            encoder=ShadowsocksEncryptionWrapperEncoder(
                encrypt_method=config.cipher_method,
                password=config.password,
                encript_mode=True),
        )

    def create_unpacker(self):
        return StreamPacker(
            encoder=ShadowsocksEncryptionWrapperEncoder(
                encrypt_method=config.cipher_method,
                password=config.password,
                encript_mode=False),
        )


