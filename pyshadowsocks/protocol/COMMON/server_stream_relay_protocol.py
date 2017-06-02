#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#

import asyncio
import concurrent.futures
from abc import abstractmethod, ABCMeta
from argparse import Namespace

import constants
from protocol.COMMON.base_server_relay_protocol import BaseServerRelayProtocal
from settings import PROTO_LOG


class ServerStreamRelayProtocol(BaseServerRelayProtocal, metaclass=ABCMeta):
    def __init__(self, loop, config: Namespace = None):
        super(ServerStreamRelayProtocol, self).__init__(loop, config)
        self.client = None

    def create_encoder(self):
        return None

    def create_decoder(self):
        return None

    @asyncio.coroutine
    def set_up_relay(self, addr, port, **kwargs):
        if not self.client:
            assert (addr is not None and port is not None)
            try:
                client = self.get_relay_protocal()
                fut = self.loop.create_connection(
                    lambda: client,
                    addr,
                    port,
                    **kwargs)

                _, self.client = yield from asyncio.wait_for(fut, constants.RELAY_CONNECT_TIMEOUT, loop=self.loop)
            except (ConnectionError, concurrent.futures.TimeoutError):
                PROTO_LOG.exception('Fail to set up connection to %s:%d', addr, port)
                return False
            else:
                PROTO_LOG.info('Connection to {}'.format(self.client.transport.get_extra_info('peername')))
                return True

        else:
            PROTO_LOG.warn('client(%s) alreader exist!', self.client.__repr__)
            return True

    def data_received_from_remote(self, client, data: bytes):
        """You can add your header before header"""
        if self.encoder:
            data = self.encoder.encode(data)
        self.transport.write(data)

    @abstractmethod
    def data_received(self, data):
        if self.decoder:
            data = self.decoder.decode(data)
            #
            # if self.client:
            #     asyncio.Task(self.send_data_to_remote(self.client, data), loop=self.loop)
            # else:
            #     asyncio.Task(self.set_up_relay('example.com', 80), loop=self.loop)

    def connection_lost_from_remote(self, client, *args):
        # the client arguments equals to self.client
        self.client = None
        self.transport.close()

    def connection_lost(self, exc):
        if self.client:
            self.client.transport.close()


if __name__ == '__main__':
    pass
