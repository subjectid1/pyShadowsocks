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
from config import PROTO_LOG
from protocal.shadowsocks.encoder import ShadowsocksEncryptionWrapperEncoder
from protocal.shadowsocks.header import ShadowsocksHeader
from protocal.streampacker import StreamPacker


class Client(asyncio.Protocol):
    def __init__(self, data_callback, conn_lost_callback):
        super(Client, self).__init__()
        self.data_callback = data_callback
        self.conn_lost_callback = conn_lost_callback

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        self.data_callback(data)

    def connection_lost(self, *args):
        self.conn_lost_callback(*args)


class ShadowsocksTCPServerProtocol(asyncio.Protocol):
    def __init__(self, loop):
        super(ShadowsocksTCPServerProtocol, self).__init__()
        self.unpacker = StreamPacker(
            header_type=ShadowsocksHeader,
            encoder=ShadowsocksEncryptionWrapperEncoder(
                encrypt_method=config.cipher_method,
                password=config.password,
                encript_mode=False),
        )
        self.packer = StreamPacker(
            header_type=ShadowsocksHeader,
            encoder=ShadowsocksEncryptionWrapperEncoder(
                encrypt_method=config.cipher_method,
                password=config.password,
                encript_mode=True),
        )

        self.transport = None
        self.loop = loop
        self.client = None

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        PROTO_LOG.info('Connection from {}'.format(peername))
        self.transport = transport

    @asyncio.coroutine
    def send_data_to_remote(self, header, raw_data):
        if not self.client and self.header:
            protocol, self.client = yield from self.loop.create_connection(
                lambda: Client(self.data_received_from_remote, self.connection_lost_from_remote),
                header.addr,
                header.port)
        elif self.client:
            self.client.transport.write(raw_data)

    def data_received_from_remote(self, data):
        # no need to send back the header
        encoded_data = self.packer.pack(data=data)
        self.transport.write(encoded_data)

    def connection_lost_from_remote(self, *args):
        # fail from remote
        self.transport.close()

    def data_received(self, data):
        header, raw_data = self.unpacker.unpack(data)
        if header:
            self.header = header
            assert (isinstance(self.header, ShadowsocksHeader))

        asyncio.Task(self.send_data_to_remote(header, raw_data))

    def connection_lost(self, exc):
        pass


if __name__ == '__main__':
    pass
