#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#

import asyncio

from abc import abstractmethod, ABCMeta
from settings import PROTO_LOG
from protocal.COMMON.base_protocal import BaseServerProtocal
from protocal.COMMON.client_relay_protocal import SimpleClientRelayProtocol


class ServerRelayProtocol(BaseServerProtocal, metaclass=ABCMeta):
    def __init__(self, loop):
        super(ServerRelayProtocol, self).__init__(loop)

        self.client = None

        self.decoder = self.create_decoder()
        self.encoder = self.create_encoder()

    @abstractmethod
    def create_encoder(self):
        raise NotImplementedError()

    @abstractmethod
    def create_decoder(self):
        raise NotImplementedError()

    @abstractmethod
    def get_relay_protocal(self):
        return SimpleClientRelayProtocol

    @asyncio.coroutine
    def send_data_to_remote(self, data):
        if not self.client:
            PROTO_LOG.warn('send data before connection setup!')
            return

        if data is None or len(data) == 0:
            PROTO_LOG.info('get null data from client {}'.format(
                self.client.transport.get_extra_info('peername'))
            )
        else:
            self.client.send_data(data)

    @asyncio.coroutine
    def set_up_relay(self, addr: str, port: int):
        if not self.client:
            assert (addr is not None and port is not None)
            _, self.client = yield from self.loop.create_connection(
                lambda: self.get_relay_protocal()(self.data_received_from_remote,
                                                  self.connection_lost_from_remote),
                addr,
                port)
            PROTO_LOG.info('Connection to {}'.format(self.client.transport.get_extra_info('peername')))
            return self.client.transport.get_extra_info('peername')

        else:
            PROTO_LOG.warn('client(%s) alreader exist!', self.client.__repr__)
            return self.client.transport.get_extra_info('peername')

    def data_received_from_remote(self, data: bytes):
        """You can add your header before header"""
        if self.encoder:
            data = self.encoder.encode(data)
        self.transport.write(data)

    @abstractmethod
    def data_received(self, data):
        if self.decoder:
            data = self.decoder.decode(data)

        if self.client:
            asyncio.Task(self.send_data_to_remote(data), loop=self.loop)
        else:
            asyncio.Task(self.set_up_relay('example.com', 80), loop=self.loop)

    def connection_lost_from_remote(self, *args):
        self.client = None
        self.transport.close()

    def connection_lost(self, exc):
        if self.client:
            self.client.transport.close()


if __name__ == '__main__':
    pass
