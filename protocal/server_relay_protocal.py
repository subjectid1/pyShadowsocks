#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#

import asyncio

from abc import abstractmethod, ABCMeta
from config import PROTO_LOG
from packet.packet_header import PacketHeader
from protocal.client_relay_protocal import ClientRelayProtocol
from protocal.shadowsocks.header import ShadowsocksPacketHeader


class ServerRelayProtocol(asyncio.Protocol, metaclass=ABCMeta):
    def __init__(self, loop):
        super(ServerRelayProtocol, self).__init__()
        self.unpacker = self.create_unpacker()
        self.packer = self.create_packer()

        self.loop = loop
        self.transport = None
        self.client = None
        self.out_data_buffer = b''

    @abstractmethod
    def create_packer(self):
        return None

    @abstractmethod
    def create_unpacker(self):
        return None

    @abstractmethod
    def get_relay_protocal(self):
        return ClientRelayProtocol

    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        PROTO_LOG.info('Connection from {}'.format(peername))
        self.transport = transport

    @asyncio.coroutine
    def send_data_to_remote(self, header, data):
        if not self.client:
            PROTO_LOG.warn('send data before connection setup!')
            return

        if data is None or len(data) == 0:
            PROTO_LOG.info('get null data from client {}'.format(
                self.client.transport.get_extra_info('peername'))
            )
        else:
            self.client.send_data(header, data)

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
        else:
            PROTO_LOG.warn('client(%s) alreader exist!', self.client.__repr__)

    @abstractmethod
    def data_received_from_remote(self, header: PacketHeader, data: bytes):
        """You can add your header before header"""
        if header:
            data = header.to_bytes() + data

        encoded_data = self.packer.pack(header=None, data=data)
        self.transport.write(encoded_data)

    @abstractmethod
    def data_received(self, data):
        header, raw_data = self.unpacker.unpack(header=ShadowsocksPacketHeader(), data=data)

        if self.client:
            # TODO: inspect the relay client' connection status, try to reconnect if disconn
            asyncio.Task(self.send_data_to_remote(None, raw_data), loop=self.loop)
        else:
            asyncio.Task(self.set_up_relay(header.addr, header.port), loop=self.loop)

    def connection_lost_from_remote(self, *args):
        self.client = None
        self.transport.close()

    def connection_lost(self, exc):
        if self.client:
            self.client.transport.close()


if __name__ == '__main__':
    pass
