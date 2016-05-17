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
from argparse import Namespace
from socket import socketpair

import constants
import encrypt
from protocol.shadowsocks.stream_server import ShadowsocksServerStreamRelayProtocol
from protocol.shadowsocks.socks5_server import ShadowsocksSOCKS5ServerProtocol
from protocol.socks5.socks5_client import SOCKS5ConnectProtocol


class ShadowsocksSOCKS5ServerTest(unittest.TestCase):
    def test(self):
        # Create a pair of connected sockets
        lsock, rsock = socketpair()
        loop = asyncio.get_event_loop()

        _args = {constants.ARG_CIPHER_METHOD: encrypt.CRYPTO_AES_256_CFB,
                 constants.ARG_PASSWORD: '123456',
                 constants.ARG_REMOTE_HOST: '127.0.0.1',
                 constants.ARG_REMOTE_PORT: 9002}
        local_config = Namespace(**_args)

        _args = {constants.ARG_CIPHER_METHOD: encrypt.CRYPTO_AES_256_CFB,
                 constants.ARG_PASSWORD: '123456',
                 constants.ARG_LISTEN_PORT: 9002}
        retmote_config = Namespace(**_args)

        coro = loop.create_server(lambda: ShadowsocksServerStreamRelayProtocol(loop, retmote_config),
                                  '127.0.0.1',
                                  retmote_config.listen_port)

        server = loop.run_until_complete(coro)

        # Register the socket to wait for data
        connect_coro = loop.create_connection(lambda: ShadowsocksSOCKS5ServerProtocol(loop, local_config), sock=rsock)
        _, server_protocol = loop.run_until_complete(connect_coro)

        def data_callback(data):
            self.assertEqual(data[:4], b'HTTP')
            lsock.close()
            rsock.close()
            # Stop the event loop
            loop.stop()

        def conneted_callback(client_protocol):
            http_request_content = b'GET / HTTP/1.1\r\nHost: example.com\r\nUser-Agent: curl/7.43.0\r\nAccept: */*\r\n\r\n'
            client_protocol.send_stream(http_request_content)

        connect_coro = loop.create_connection(
            lambda: SOCKS5ConnectProtocol(loop, 'example.com', 80, conneted_callback, data_callback), sock=lsock)

        _, client_protocol = loop.run_until_complete(connect_coro)
        client_protocol.start()

        # Simulate the reception of data from the network
        # loop.call_soon(rsock.send, encoded_data)
        # Run the event loop

        loop.run_forever()
