#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
from abc import abstractmethod
from typing import Callable

from packet.packet_header import PacketHeader
from protocal.COMMON.client_relay_protocal import SimpleClientRelayProtocol


class CommonClientRelayProtocal(SimpleClientRelayProtocol):
    def __init__(self, data_callback: Callable[[PacketHeader, bytes], None], conn_lost_callback):
        super(CommonClientRelayProtocal, self).__init__(data_callback, conn_lost_callback)
        self.decoder = self.create_decoder()
        self.encoder = self.create_encoder()

    @abstractmethod
    def create_encoder(self):
        raise NotImplementedError()

    @abstractmethod
    def create_decoder(self):
        raise NotImplementedError()

    def send_data(self, data: bytes):
        if self.encoder:
            data = self.encoder.encode(data)

        super(CommonClientRelayProtocal, self).send_data(data)

    def data_received(self, data):
        if self.decoder:
            data = self.decoder.decode(data)

        super(CommonClientRelayProtocal, self).data_received(data)
