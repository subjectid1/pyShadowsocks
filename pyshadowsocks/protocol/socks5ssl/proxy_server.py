#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info: asyncio  - Stream <https://docs.python.org/3/library/asyncio-stream.html#asyncio-tcp-echo-server-streams>
#                - Transport <https://docs.python.org/3/library/asyncio-protocol.html>
#                - relay in data_received: https://stackoverflow.com/questions/21295068/how-can-i-create-a-relay-server-using-tulip-asyncio-in-python/21297354#21297354
#

from protocol.socks5.socks5_server import SOCKS5ServerStreamProtocol


class SOCKS5SSLProxyServerProtocol(SOCKS5ServerStreamProtocol):
    def __init__(self, loop, config):
        super(SOCKS5SSLProxyServerProtocol, self).__init__(loop, config)
