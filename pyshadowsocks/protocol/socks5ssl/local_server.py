#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
#
#
import asyncio
from argparse import Namespace

from protocol.COMMON.server_stream_relay_protocol import ServerStreamRelayProtocol
from protocol.socks5ssl import create_client_ssl_context


class SOCKS5SSLLocalServerProtocol(ServerStreamRelayProtocol):
    def __init__(self, loop, config: Namespace = None):
        super(SOCKS5SSLLocalServerProtocol, self).__init__(loop, config)

        self.proxy_server = self.config.remote_host
        self.proxy_port = self.config.remote_port

        self._buffer = b''
        self._connected = False

    def connection_made(self, transport):
        super(SOCKS5SSLLocalServerProtocol, self).connection_made(transport)

        f = asyncio.ensure_future(self.set_up_relay(self.proxy_server, self.proxy_port,
                                                    ssl=create_client_ssl_context()), loop=self.loop)

        def send_buffer(fut):
            self._connected = fut.result()
            if self._connected and len(self._buffer) > 0:
                asyncio.ensure_future(self.send_data_to_remote(self.client, self._buffer), loop=self.loop)
                self._buffer = None

        f.add_done_callback(send_buffer)

    def data_received(self, data):
        if self._connected:
            asyncio.ensure_future(self.send_data_to_remote(self.client, data), loop=self.loop)
        else:
            self._buffer += data
