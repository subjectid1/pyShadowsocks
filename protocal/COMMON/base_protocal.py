#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
import asyncio

import settings


class BaseProtocol(asyncio.Protocol):
    def __init__(self):
        super(BaseProtocol, self).__init__()

        self.transport = None

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        settings.PROTO_LOG.info('Connection from {}'.format(peername))
        self.transport = transport


class BaseServerProtocal(BaseProtocol):
    def __init__(self, loop):
        super(BaseServerProtocal, self).__init__()
        self.loop = loop
