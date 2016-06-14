#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
#
import os.path
import sys

sys.path.insert(0, os.path.dirname(__file__))

import asyncio
import constants
import settings
from protocol.socks5ssl import create_server_ssl_context
from protocol.socks5ssl.local_server import SOCKS5SSLLocalServerProtocol
from protocol.socks5ssl.proxy_server import SOCKS5SSLProxyServerProtocol
from pac.http_server import FakePACGetProtocol
from protocol.shadowsocks.proxy_server import ShadowsocksProxyServerProtocol
from protocol.shadowsocks.local_server import ShadowsocksLocalServerProtocol
from util.config import parse_args_new
from util.resc import set_open_file_limit_up_to


def main():
    soft, hard = set_open_file_limit_up_to(0xffff)
    settings.CONFIG_LOG.info('open file limit set to %d:%d', soft, hard)

    ns = parse_args_new()
    loop = asyncio.get_event_loop()

    if ns.protocol_mode == constants.ARG_PROTOCOL_SHADOWSOCKS:
        if ns.server_mode == constants.ARG_LOCAL_SERVER:
            # Each client connection will create a new protocol instance
            coro = loop.create_server(
                lambda: ShadowsocksLocalServerProtocol(loop, config=ns),
                '0.0.0.0',
                ns.socks_port)
            server = loop.run_until_complete(coro)

        elif ns.server_mode == constants.ARG_REMOTE_SERVER:
            loop = asyncio.get_event_loop()
            # Each client connection will create a new protocol instance
            coro = loop.create_server(
                lambda: ShadowsocksProxyServerProtocol(loop, config=ns),
                '0.0.0.0',
                ns.listen_port)
            server = loop.run_until_complete(coro)

    elif ns.protocol_mode == constants.ARG_PROTOCOL_SOCKS5OVERSSL:
        if ns.server_mode == constants.ARG_LOCAL_SERVER:
            coro = loop.create_server(
                lambda: SOCKS5SSLLocalServerProtocol(loop, config=ns),
                '0.0.0.0',
                ns.socks_port)
            server = loop.run_until_complete(coro)

        elif ns.server_mode == constants.ARG_REMOTE_SERVER:
            coro = loop.create_server(
                lambda: SOCKS5SSLProxyServerProtocol(loop, config=ns),
                '0.0.0.0',
                ns.listen_port,
                ssl=create_server_ssl_context())
            server = loop.run_until_complete(coro)

    if ns.server_mode == constants.ARG_LOCAL_SERVER and ns.pac_port:
        coro = loop.create_server(FakePACGetProtocol, '127.0.0.1', ns.pac_port)
        server = loop.run_until_complete(coro)

    loop.run_forever()


if __name__ == '__main__':
    main()
