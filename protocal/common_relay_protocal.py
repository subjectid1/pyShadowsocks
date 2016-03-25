#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
from typing import Callable

from packet.packet_header import PacketHeader
from protocal.client_relay_protocal import ClientRelayProtocol


class CommonClientRelayProtocal(ClientRelayProtocol):
    def __init__(self, data_callback: Callable[[PacketHeader, bytes], None], conn_lost_callback):
        super(CommonClientRelayProtocal, self).__init__(data_callback, conn_lost_callback)
        self.unpacker = self.create_unpacker()
        self.packer = self.create_packer()

    def create_packer(self):
        raise NotImplementedError()

    def create_unpacker(self):
        raise NotImplementedError()

    def send_data(self, header: PacketHeader, data: bytes):
        data = self.packer.pack(header, data)
        self.transport.write(data)

    def data_received(self, data):
        header, data = self.unpacker.unpack(None, data)
        self.data_callback(header, data)
