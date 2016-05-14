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
from protocol.COMMON.simple_client_relay_protocol import SimpleClientRelayProtocol


class CommonClientRelayProtocol(SimpleClientRelayProtocol):
    def __init__(self, data_callback, conn_lost_callback,
                 config: Namespace = None):
        super(CommonClientRelayProtocol, self).__init__(data_callback, conn_lost_callback)
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

        super(CommonClientRelayProtocol, self).send_data(data)

    def data_received(self, data):
        if self.decoder:
            data = self.decoder.decode(data)

        super(CommonClientRelayProtocol, self).data_received(data)
