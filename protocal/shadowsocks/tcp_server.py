#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info: asyncio  - Stream <https://docs.python.org/3/library/asyncio-stream.html#asyncio-tcp-echo-server-streams>
#                - Transport <https://docs.python.org/3/library/asyncio-protocol.html>
#                - relay in data_received: https://stackoverflow.com/questions/21295068/how-can-i-create-a-relay-server-using-tulip-asyncio-in-python/21297354#21297354
#
import asyncio

import config
from protocal.packet_header import PacketHeader
from protocal.server_relay_protocal import ServerRelayProtocol
from protocal.shadowsocks.encoder import ShadowsocksEncryptionWrapperEncoder
from protocal.shadowsocks.header import ShadowsocksPacketHeader
from protocal.stream_packer import StreamPacker


class ShadowsocksTCPServerRelayProtocol(ServerRelayProtocol):
    def __init__(self, loop):
        super(ShadowsocksTCPServerRelayProtocol, self).__init__(loop)
        self.header = None

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

    def get_relay_protocal(self):
        return super(ShadowsocksTCPServerRelayProtocol, self).get_relay_protocal()

    def data_received_from_remote(self, header: PacketHeader, data: bytes):
        return super(ShadowsocksTCPServerRelayProtocol, self).data_received_from_remote(header, data)

    def data_received(self, data):
        if not self.header:
            self.header, raw_data = self.unpacker.unpack(header=ShadowsocksPacketHeader(), data=data)
            if not self.header:
                return
        else:
            _, raw_data = self.unpacker.unpack(header=None, data=data)
            if not raw_data:
                return

        if self.client:
            asyncio.ensure_future(self.send_data_to_remote(None, raw_data), loop=self.loop)
        else:
            # TODO: run two task one by one, using the simplier styly
            f = asyncio.ensure_future(self.set_up_relay(self.header.addr, self.header.port), loop=self.loop)

            def send_data(_):
                asyncio.ensure_future(self.send_data_to_remote(None, raw_data), loop=self.loop)

            f.add_done_callback(send_data)


if __name__ == '__main__':
    pass
