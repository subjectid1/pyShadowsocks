#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: 
# 
# Info:
#
#
import asyncio

import constants
import settings
from protocol.shadowsocks.socks5_server import ShadowsocksSOCKS5ServerProtocol
from util.config import parse_args

if __name__ == '__main__':
    for key, value in parse_args(is_local=True).items():
        setattr(settings, key, value)

    if settings.protocol == constants.PROTOCOL_SHADOWSOCKS:
        loop = asyncio.get_event_loop()
        # Each client connection will create a new protocol instance
        coro = loop.create_server(
            lambda: ShadowsocksSOCKS5ServerProtocol(loop, settings.remote_host, settings.remote_port),
            '0.0.0.0',
            settings.listen_port)

        server = loop.run_until_complete(coro)
        loop.run_forever()
