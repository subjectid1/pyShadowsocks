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
from protocal.shadowsocks.encoder import ShadowsocksEncryptionWrapperEncoder
from protocal.shadowsocks.header import ShadowsocksHeader
from protocal.shadowsocks.tcp_server import ShadowsocksTCPServerProtocol
from protocal.streampacker import StreamPacker




class ShadowsocksTCPServerTest(unittest.TestCase):
    def test_data_received(self):
        # Create a pair of connected sockets
        rsock, wsock = socketpair()
        loop = asyncio.get_event_loop()



        # Register the socket to wait for data
        connect_coro = loop.create_connection(lambda :ShadowsocksTCPServerProtocol(loop), sock=rsock)
        transport, protocol = loop.run_until_complete(connect_coro)

        packer = StreamPacker(
            header_type=ShadowsocksHeader,
            encoder=ShadowsocksEncryptionWrapperEncoder(
                encrypt_method=config.cipher_method,
                password=config.password,
                encript_mode=True),
        )
        protocol.loop = loop
        header = ShadowsocksHeader(addr='example.com', port=80, addr_type=constants.ADDRTYPE_HOST)
        http_request_content = b'GET / HTTP/1.1\r\nHost: example.com\r\nUser-Agent: curl/7.43.0\r\nAccept: */*\r\n\r\n'

        # Simulate the reception of data from the network
        encoded_data = packer.pack(header, http_request_content)
        loop.call_soon(wsock.send, encoded_data)


        # Run the event loop
        loop.run_forever()

        # We are done, close sockets and the event loop
        rsock.close()
        wsock.close()
        loop.close()

    def test2(self):
        import asyncio
        try:
            from socket import socketpair
        except ImportError:
            from asyncio.windows_utils import socketpair

        # Create a pair of connected sockets
        rsock, wsock = socketpair()
        loop = asyncio.get_event_loop()

        class MyProtocol(asyncio.Protocol):
            transport = None

            def connection_made(self, transport):
                self.transport = transport

            def data_received(self, data):
                print("Received:", data.decode())

                # We are done: close the transport (it will call connection_lost())
                self.transport.close()

            def connection_lost(self, exc):
                # The socket has been closed, stop the event loop
                loop.stop()

        # Register the socket to wait for data
        connect_coro = loop.create_connection(MyProtocol, sock=rsock)
        transport, protocol = loop.run_until_complete(connect_coro)

        # Simulate the reception of data from the network
        loop.call_soon(wsock.send, 'abc'.encode())

        # Run the event loop
        loop.run_forever()

        # We are done, close sockets and the event loop
        rsock.close()
        wsock.close()
        loop.close()
