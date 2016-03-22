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
from protocal.shadowsocks.tcp_relay import TCPRelay
from protocal.streampacker import StreamPacker


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

        self.loop = loop
        self.transport = None
        self.client = None

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        PROTO_LOG.info('Connection from {}'.format(peername))
        self.transport = transport

    @asyncio.coroutine
    def send_data_to_remote(self, header, raw_data):
        if not self.client:
            if header:
                _, self.client = yield from self.loop.create_connection(
                    lambda: TCPRelay(self.data_received_from_remote,
                                     self.connection_lost_from_remote),
                    header.addr,
                    header.port)
                PROTO_LOG.info('Connection to {}'.format(self.client.transport.get_extra_info('peername')))
                self.client.transport.write(raw_data)
            else:
                PROTO_LOG.error('where is the header?')
                self.transport.close()

        else:
            if raw_data is None or len(raw_data) == 0:
                PROTO_LOG.info('get null data from client {}'.format(
                    self.client.transport.get_extra_info('peername'))
                )
            else:
                self.client.transport.write(raw_data)

    def data_received_from_remote(self, data):
        encoded_data = self.packer.pack(data=data, header=None)
        self.transport.write(encoded_data)

    def connection_lost_from_remote(self, *args):
        self.client = None
        self.transport.close()

    def data_received(self, data):
        header, raw_data = self.unpacker.unpack(data, has_header=True)
        asyncio.Task(self.send_data_to_remote(header, raw_data), loop=self.loop)

    def connection_lost(self, exc):
        if self.client:
            self.client.transport.close()


if __name__ == '__main__':
    pass
