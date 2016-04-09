#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
from argparse import Namespace
from typing import Callable

from abc import abstractmethod
from packet.packet_header import PacketHeader
from protocol.COMMON.client_relay_protocal import SimpleClientRelayProtocol


class CommonClientRelayProtocal(SimpleClientRelayProtocol):
    def __init__(self, data_callback: Callable[[PacketHeader, bytes], None], conn_lost_callback,
                 config: Namespace = None):
        super(CommonClientRelayProtocal, self).__init__(data_callback, conn_lost_callback)
        self.config = config
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
