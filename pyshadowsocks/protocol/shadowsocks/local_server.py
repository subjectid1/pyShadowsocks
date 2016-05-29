#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
#
#
import asyncio
from argparse import Namespace

import constants
from protocol.shadowsocks.client import ShadowsocksClientRelayProtocol
from protocol.socks5.header import Socks5AddrHeader
from protocol.socks5.socks5_server import SOCKS5ServerStreamProtocol


class ShadowsocksLocalServerProtocol(SOCKS5ServerStreamProtocol):
    def __init__(self, loop, config: Namespace = None):
        super(ShadowsocksLocalServerProtocol, self).__init__(loop, config)

        self.proxy_server = self.config.remote_host
        self.proxy_port = self.config.remote_port

        self.is_first_packet_sent = False

    def get_relay_protocal(self):
        return ShadowsocksClientRelayProtocol(self.data_received_from_remote,
                                              self.connection_lost_from_remote,
                                              self.config)

    async def connect_to_addr_tcp(self, addr: Socks5AddrHeader):
        ret = await self.set_up_relay(self.proxy_server, self.proxy_port)
        if ret:
            return True, (self.client.transport.get_extra_info('sockname'))
        else:
            return False, (None, None)


    def data_received(self, data):
        if self.sock5_processor.get_state() == constants.STAGE_SOCKS5_TCP_RELAY:
            if not self.is_first_packet_sent:
                data = self.sock5_processor.tcp_session_target_addr.to_bytes() + data
                self.is_first_packet_sent = True

            asyncio.ensure_future(self.send_data_to_remote(self.client, data), loop=self.loop)
        else:
            super(ShadowsocksLocalServerProtocol, self).data_received(data)
