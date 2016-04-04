#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
#
# Info: asyncio  - Stream <https://docs.python.org/3/library/asyncio-stream.html#asyncio-tcp-echo-server-streams>
#                - Transport <https://docs.python.org/3/library/asyncio-protocol.html>
#                - relay in data_received: https://stackoverflow.com/questions/21295068/how-can-i-create-a-relay-server-using-tulip-asyncio-in-python/21297354#21297354
#
import asyncio

from protocal.COMMON.client_relay_protocal import SimpleClientRelayProtocol
from protocal.COMMON.server_relay_protocal import ServerRelayProtocol
from protocal.shadowsocks.header import Socks5AddrHeader
from protocal.socks5.socks5_processor import Socks5Processor


class SOCKS5ServerProtocol(ServerRelayProtocol):
    def __init__(self, loop):
        super(SOCKS5ServerProtocol, self).__init__(loop)
        self.addr_header = None
        self.sock5_processor = None

    def create_encoder(self):
        return None

    def create_decoder(self):
        return None

    def get_relay_protocal(self):
        return SimpleClientRelayProtocol

    def data_received(self, data):

        if not self.sock5_processor:
            async def connect_to_addr(addr: Socks5AddrHeader):
                remote_addr, remote_port = await self.set_up_relay(addr.addr, addr.port)
                return remote_addr, remote_port

            self.sock5_processor = Socks5Processor(self.loop, self.transport, connect_to_addr)

        if not self.sock5_processor.socks_connected():
            self.sock5_processor.do_request(data)

        elif self.sock5_processor.socks_connected():
            # streaming data now
            if not self.addr_header:
                self.addr_header = self.sock5_processor._connected_addr

            asyncio.ensure_future(self.send_data_to_remote(data), loop=self.loop)


if __name__ == '__main__':
    pass
