#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
import asyncio

import constants
import settings
from protocol.shadowsocks.server import ShadowsocksServerRelayProtocol
from util.config import parse_args

if __name__ == '__main__':
    for key, value in parse_args(is_local=False).items():
        setattr(settings, key, value)

    if settings.protocol == constants.PROTOCOL_SHADOWSOCKS:
        loop = asyncio.get_event_loop()
        # Each client connection will create a new protocol instance
        coro = loop.create_server(lambda: ShadowsocksServerRelayProtocol(loop), '127.0.0.1', settings.listen_port)
        server = loop.run_until_complete(coro)
        loop.run_forever()
