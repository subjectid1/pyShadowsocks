#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
import asyncio


class TCPRelay(asyncio.Protocol):
    def __init__(self, data_callback, conn_lost_callback):
        super(TCPRelay, self).__init__()
        self.data_callback = data_callback
        self.conn_lost_callback = conn_lost_callback

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        self.data_callback(data)

    def connection_lost(self, *args):
        self.conn_lost_callback(*args)