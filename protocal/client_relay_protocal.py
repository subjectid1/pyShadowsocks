#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
import asyncio
from typing import Callable

from packet.packet_header import PacketHeader


class ClientRelayProtocol(asyncio.Protocol):
    def __init__(self, data_callback: Callable[[PacketHeader, bytes], None], conn_lost_callback):
        super(ClientRelayProtocol, self).__init__()
        self.data_callback = data_callback
        self.conn_lost_callback = conn_lost_callback
        self.transport = None

    def send_data(self, header: PacketHeader, data: bytes):
        """You can add addional header before header, String them together"""
        if header is not None:
            self.transport.write(header.to_bytes() + data)
        else:
            return self.transport.write(data)

    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        self.data_callback(None, data)

    def connection_lost(self, *args):
        self.conn_lost_callback(*args)
