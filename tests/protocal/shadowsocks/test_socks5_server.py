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

from protocal.shadowsocks.server import ShadowsocksServerRelayProtocol
from protocal.shadowsocks.socks5_server import ShadowsocksSOCKS5ServerProtocol
from protocal.socks5.socks5_client import SOCKS5ConnectProtocol


class ShadowsocksSOCKS5ServerTest(unittest.TestCase):
    def test(self):
        # Create a pair of connected sockets
        lsock, rsock = socketpair()
        loop = asyncio.get_event_loop()

        remote_server_host = '127.0.0.1'
        remote_server_port = 9001

        coro = loop.create_server(lambda :ShadowsocksServerRelayProtocol(loop), remote_server_host, remote_server_port)
        server = loop.run_until_complete(coro)

        # Register the socket to wait for data
        connect_coro = loop.create_connection(lambda: ShadowsocksSOCKS5ServerProtocol(loop, remote_server_host, remote_server_port), sock=rsock)
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
