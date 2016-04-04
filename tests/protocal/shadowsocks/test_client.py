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

import constants
from protocal.shadowsocks.client import ShadowsocksClientRelayProtocol
from protocal.shadowsocks.header import ShadowsocksPacketHeader
from protocal.shadowsocks.server import ShadowsocksServerRelayProtocol


class ShadowsocksClientTest(unittest.TestCase):
    def test_client(self):
        # Create a pair of connected sockets
        lsock, rsock = socketpair()
        loop = asyncio.get_event_loop()

        # Register the socket to wait for data
        connect_coro = loop.create_connection(lambda: ShadowsocksServerRelayProtocol(loop), sock=rsock)
        _, server_protocol = loop.run_until_complete(connect_coro)

        def data_callback(data):
            self.assertEqual(data[:4], b'HTTP')
            lsock.close()
            rsock.close()
            # Stop the event loop
            loop.stop()

        def conn_lost_callback(*args):
            pass

        connect_coro = loop.create_connection(
            lambda: ShadowsocksClientRelayProtocol(data_callback, conn_lost_callback), sock=lsock)

        _, client_protocol = loop.run_until_complete(connect_coro)

        header = ShadowsocksPacketHeader(addr='example.com', port=80, addr_type=constants.SOCKS5_ADDRTYPE_HOST)
        http_request_content = b'GET / HTTP/1.1\r\nHost: example.com\r\nUser-Agent: curl/7.43.0\r\nAccept: */*\r\n\r\n'

        client_protocol.send_data(header.to_bytes() + http_request_content)

        # Simulate the reception of data from the network
        # loop.call_soon(rsock.send, encoded_data)
        # Run the event loop

        loop.run_forever()
