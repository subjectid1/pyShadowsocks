#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
#
# Info: https://www.ietf.org/rfc/rfc1928.txt
#
import settings
from protocol.shadowsocks.client import ShadowsocksClientRelayProtocol
from protocol.socks5.header import Socks5AddrHeader
from protocol.socks5.socks5_server import SOCKS5ServerProtocol


class ShadowsocksSOCKS5ServerProtocol(SOCKS5ServerProtocol):
    def __init__(self, loop, remote_server_host: str = None, remote_server_port: int = None):
        super(ShadowsocksSOCKS5ServerProtocol, self).__init__(loop)

        self.remote_server_host = remote_server_host or settings.remote_host
        self.remote_server_port = remote_server_port or settings.remote_port

        self.target_addr_header = None

    def get_relay_protocal(self):
        return ShadowsocksClientRelayProtocol

    async def connect_to_addr(self, addr: Socks5AddrHeader):
        remote_addr, remote_port = await self.set_up_relay(self.remote_server_host, self.remote_server_port)
        return remote_addr, remote_port

    def data_received(self, data):
        if self.sock5_processor and self.sock5_processor.socks_connected() and not self.target_addr_header:
            # streaming data now
            self.target_addr_header = self.sock5_processor.connected_addr
            data = self.target_addr_header.to_bytes() + data

        super(ShadowsocksSOCKS5ServerProtocol, self).data_received(data)
