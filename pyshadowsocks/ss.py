#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
#
import sys

import os.path

sys.path.insert(0, os.path.dirname(__file__))

import asyncio
import constants
import settings
from pac.http_server import FakeHTTPGetProtocol
from protocol.shadowsocks.stream_server import ShadowsocksServerStreamRelayProtocol
from protocol.shadowsocks.socks5_server import ShadowsocksSOCKS5ServerProtocol
from util.config import parse_args_new
from util.resc import set_open_file_limit_up_to


def main():
    soft, hard = set_open_file_limit_up_to(0xffff)
    settings.CONFIG_LOG.info('open file limit set to %d:%d', soft, hard)

    ns = parse_args_new()

    if ns.protocol_mode == constants.ARG_PROTOCOL_SHADOWSOCKS:
        if ns.server_mode == constants.ARG_LOCAL_SERVER:
            loop = asyncio.get_event_loop()
            # Each client connection will create a new protocol instance
            coro = loop.create_server(
                lambda: ShadowsocksSOCKS5ServerProtocol(loop, config=ns),
                '0.0.0.0',
                ns.socks_port)
            server = loop.run_until_complete(coro)

            if ns.pac_port:
                coro = loop.create_server(FakeHTTPGetProtocol, '127.0.0.1', ns.pac_port)
                server = loop.run_until_complete(coro)

            loop.run_forever()

        elif ns.server_mode == constants.ARG_REMOTE_SERVER:
            loop = asyncio.get_event_loop()
            # Each client connection will create a new protocol instance
            coro = loop.create_server(lambda: ShadowsocksServerStreamRelayProtocol(loop, config=ns), '0.0.0.0',
                                      ns.listen_port)
            server = loop.run_until_complete(coro)
            loop.run_forever()


if __name__ == '__main__':
    main()
