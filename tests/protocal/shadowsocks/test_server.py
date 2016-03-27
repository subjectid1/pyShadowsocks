#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
import asyncio
import unittest
from socket import socketpair

import config
import constants
from packet.stream_packer import StreamPacker
from protocal.shadowsocks.encoder import ShadowsocksEncryptionWrapperEncoder
from protocal.shadowsocks.header import ShadowsocksPacketHeader
from protocal.shadowsocks.server import ShadowsocksServerRelayProtocol


class ShadowsocksTCPServerTest(unittest.TestCase):
    def test_data_relay(self):
        # Create a pair of connected sockets
        lsock, rsock = socketpair()
        loop = asyncio.get_event_loop()

        # Register the socket to wait for data
        connect_coro = loop.create_connection(lambda: ShadowsocksServerRelayProtocol(loop), sock=lsock)
        transport, protocol = loop.run_until_complete(connect_coro)

        packer = StreamPacker(
            encoder=ShadowsocksEncryptionWrapperEncoder(
                encrypt_method=config.cipher_method,
                password=config.password,
                encript_mode=True),
        )

        unpacker = StreamPacker(
            encoder=ShadowsocksEncryptionWrapperEncoder(
                encrypt_method=config.cipher_method,
                password=config.password,
                encript_mode=False),
        )

        protocol.loop = loop
        header = ShadowsocksPacketHeader(addr='example.com', port=80, addr_type=constants.SOCKS5_ADDRTYPE_HOST)
        http_request_content = b'GET / HTTP/1.1\r\nHost: example.com\r\nUser-Agent: curl/7.43.0\r\nAccept: */*\r\n\r\n'

        # Simulate the reception of data from the network
        encoded_data = packer.pack(header=header, data=http_request_content)
        loop.call_soon(rsock.send, encoded_data)

        def reader():
            data = rsock.recv(100)
            if not data or len(data) == 0:
                return

            _, http_response_content = unpacker.unpack(data=data, header=None)
            self.assertEqual(http_response_content[:4], b'HTTP')
            # We are done: unregister the file descriptor
            loop.remove_reader(rsock)
            lsock.close()
            rsock.close()
            # Stop the event loop
            loop.stop()

        # Register the file descriptor for read event
        loop.add_reader(rsock, reader)
        # Run the event loop
        loop.run_forever()
        # We are done, close sockets and the event loop
