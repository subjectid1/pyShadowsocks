#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#

import asyncio
from argparse import Namespace

from abc import abstractmethod
from protocol.COMMON.base_protocal import BaseServerProtocal
from protocol.COMMON.simple_client_relay_protocol import SimpleClientRelayProtocol
from settings import PROTO_LOG


class BaseServerRelayProtocal(BaseServerProtocal):
    def __init__(self, loop, config: Namespace = None):
        super(BaseServerRelayProtocal, self).__init__(loop, config)
        self.decoder = self.create_decoder()
        self.encoder = self.create_encoder()

    def create_encoder(self):
        raise NotImplementedError()

    def create_decoder(self):
        raise NotImplementedError()

    def get_relay_protocal(self):
        return SimpleClientRelayProtocol(self.data_received_from_remote,
                                         self.connection_lost_from_remote)

    @asyncio.coroutine
    def set_up_relay(self, addr, port):
        """

        :param target_addr: tuple: (host, port)
        :param from_addr:
        :return:
        """
        raise NotImplementedError()

    @asyncio.coroutine
    def send_data_to_remote(self, relay_client, data):
        if not relay_client:
            PROTO_LOG.warn('send data before connection setup!')
            return

        if data is None or len(data) == 0:
            PROTO_LOG.info('null data to relay')
        else:
            relay_client.send_data(data)

    @abstractmethod
    def data_received_from_remote(self, client, data: bytes):
        raise NotImplementedError()

    @abstractmethod
    def connection_lost_from_remote(self, client, *args):
        raise NotImplementedError()

    @abstractmethod
    def connection_lost(self, exc):
        raise NotImplementedError()
