#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
from typing import Callable

from protocol.COMMON.base_protocal import BaseProtocol


class SimpleClientRelayProtocol(BaseProtocol):
    def __init__(self, data_callback, conn_lost_callback):
        super(SimpleClientRelayProtocol, self).__init__()
        self.data_callback = data_callback
        self.conn_lost_callback = conn_lost_callback

    def send_data(self, data: bytes):
        return self.transport.write(data)

    def data_received(self, data):
        self.data_callback(self, data)

    def connection_lost(self, *args):
        self.conn_lost_callback(*args)
