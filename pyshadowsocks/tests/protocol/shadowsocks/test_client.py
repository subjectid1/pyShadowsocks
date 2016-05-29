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
from protocol.shadowsocks.client import ShadowsocksClientRelayProtocol
from protocol.shadowsocks.header import ShadowsocksPacketHeader
from protocol.shadowsocks.proxy_server import ShadowsocksProxyServerProtocol


class ShadowsocksClientTest(unittest.TestCase):
    def test_client(self):
        # Create a pair of connected sockets
        lsock, rsock = socketpair()
        loop = asyncio.get_event_loop()

        _args = {constants.ARG_CIPHER_METHOD: encrypt.AES_256_CFB, constants.ARG_PASSWORD: '123456'}
        config = Namespace(**_args)

        # Register the socket to wait for data
        connect_coro = loop.create_connection(lambda: ShadowsocksProxyServerProtocol(loop, config), sock=rsock)
        _, server_protocol = loop.run_until_complete(connect_coro)

        def data_callback(client, data):
            self.assertEqual(data[:4], b'HTTP')
            lsock.close()
            rsock.close()
            # Stop the event loop
            loop.stop()

        def conn_lost_callback(*args):
            pass

        connect_coro = loop.create_connection(
            lambda: ShadowsocksClientRelayProtocol(data_callback, conn_lost_callback, config), sock=lsock)

        _, client_protocol = loop.run_until_complete(connect_coro)

        header = ShadowsocksPacketHeader(addr='example.com', port=80, addr_type=constants.SOCKS5_ADDRTYPE_HOST)
        http_request_content = b'GET / HTTP/1.1\r\nHost: example.com\r\nUser-Agent: curl/7.43.0\r\nAccept: */*\r\n\r\n'

        client_protocol.send_data(header.to_bytes() + http_request_content)

        # Simulate the reception of data from the network
        # loop.call_soon(rsock.send, encoded_data)
        # Run the event loop

        loop.run_forever()
