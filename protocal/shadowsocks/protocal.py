#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info: asyncio  - Stream<https://docs.python.org/3/library/asyncio-stream.html#asyncio-tcp-echo-server-streams>
#                - Transport<https://docs.python.org/3/library/asyncio-protocol.html>
#

import asyncio

import config
from config import PROTO_LOG
from protocal.shadowsocks.encoder import ShadowsocksEncryptionWrapperEncoder
from protocal.shadowsocks.header import ShadowsocksHeader
from protocal.streampacker import StreamPacker


class ShadowsocksTCPServerProtocol(asyncio.Protocol):
    def __init__(self):
        self.decoder = StreamPacker(
            header_type=ShadowsocksHeader,
            encoder=ShadowsocksEncryptionWrapperEncoder(
                encrypt_method=config.cipher_method,
                password=config.password,
                encript_mode=False),
        )
        self.encoder = StreamPacker(
            header_type=ShadowsocksHeader,
            encoder=ShadowsocksEncryptionWrapperEncoder(
                encrypt_method=config.cipher_method,
                password=config.password,
                encript_mode=True),
        )

        self.transport = None
        self.header = None
        self.remote_sock = None

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        PROTO_LOG.info('Connection from {}'.format(peername))
        self.transport = transport

    def connection_lost(self, exc):
        pass

    def data_received(self, data):
        try:
            header, raw_data = self.decoder.unpack(data)
            if header:
                self.header = header
                # forward TCP
                self.remote_sock = None
                # data return from remote
                raw_data = raw_data

            # no need to send back the header
            encoded_data = self.encoder.pack(data=raw_data)
            self.transport.write(encoded_data)

        except Exception:
            PROTO_LOG.error('decode data %s fail!, transport from %s close!',
                            data,
                            self.transport.get_extra_info('peername'))
            self.transport.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # Each client connection will create a new protocol instance
    coro = loop.create_server(ShadowsocksTCPServerProtocol, '127.0.0.1', 8888)
    server = loop.run_until_complete(coro)

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
