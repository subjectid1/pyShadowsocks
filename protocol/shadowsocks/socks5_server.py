#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
#
# Info: https://www.ietf.org/rfc/rfc1928.txt
#
from argparse import Namespace

import functools
from protocol.shadowsocks.client import ShadowsocksClientRelayProtocol
from protocol.socks5.header import Socks5AddrHeader
from protocol.socks5.socks5_server import SOCKS5ServerProtocol


class ShadowsocksSOCKS5ServerProtocol(SOCKS5ServerProtocol):
    def __init__(self, loop, config: Namespace = None):
        super(ShadowsocksSOCKS5ServerProtocol, self).__init__(loop, config)

        self.remote_server_host = self.config.remote_host
        self.remote_server_port = self.config.remote_port

        self.target_addr_header = None

    def get_relay_protocal(self):
        return ShadowsocksClientRelayProtocol(functools.partial(self.data_received_from_remote),
                                              self.connection_lost_from_remote,
                                              self.config)

    async def connect_to_addr(self, addr: Socks5AddrHeader):
        remote_addr, remote_port = await self.set_up_relay(self.remote_server_host, self.remote_server_port)
        return remote_addr, remote_port

    def data_received(self, data):
        if self.sock5_processor and self.sock5_processor.socks_connected() and not self.target_addr_header:
            # streaming data now
            self.target_addr_header = self.sock5_processor.connected_addr
            data = self.target_addr_header.to_bytes() + data

        super(ShadowsocksSOCKS5ServerProtocol, self).data_received(data)
