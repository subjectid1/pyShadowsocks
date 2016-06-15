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
from protocol.socks5.socks5_client import SOCKS5ConnectProtocol
from protocol.socks5.socks5_server import SOCKS5ServerStreamProtocol


class SOCKS5ServerTest(unittest.TestCase):
    def test(self):
        # Create a pair of connected sockets
        lsock, rsock = socketpair()
        loop = asyncio.get_event_loop()

        _args = {constants.ARG_USERNAME: 'user',
                 constants.ARG_PASSWORD: '123456'}
        retmote_config = Namespace(**_args)

        # Register the socket to wait for data
        connect_coro = loop.create_connection(lambda: SOCKS5ServerStreamProtocol(loop, config=retmote_config),
                                              sock=rsock)
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

        # connect_coro1 = loop.create_connection(
        #     lambda: SOCKS5ConnectProtocol(loop, 'example.com', 80, conneted_callback, data_callback),
        #     sock=lsock)

        connect_coro2 = loop.create_connection(
            lambda: SOCKS5ConnectProtocol(loop, 'example.com', 80, conneted_callback, data_callback,
                                          user='user', password='123456'),
            sock=lsock)

        # loop.run_until_complete(connect_coro1)
        loop.run_until_complete(connect_coro2)

        # Simulate the reception of data from the network
        # loop.call_soon(rsock.send, encoded_data)
        # Run the event loop

        loop.run_forever()
