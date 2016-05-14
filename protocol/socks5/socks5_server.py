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
from argparse import Namespace

import constants
import functools
from protocol.COMMON.server_stream_relay_protocol import ServerStreamRelayProtocol
from protocol.socks5.header import Socks5AddrHeader
from protocol.socks5.socks5_processor import Socks5Processor


class SOCKS5ServerStreamProtocol(ServerStreamRelayProtocol):
    def connection_made(self, transport):
        super(SOCKS5ServerStreamProtocol, self).connection_made(transport)
        self.sock5_processor = Socks5Processor(self.loop,
                                               self.transport,
                                               functools.partial(self.connect_to_addr_tcp),
                                               functools.partial(self.connect_to_addr_udp))

    async def connect_to_addr_tcp(self, addr: Socks5AddrHeader):
        """
            In the reply to a CONNECT, BND.PORT contains the port number that the
            server assigned to connect to the target host, while BND.ADDR
            contains the associated IP address.
        """
        ret = await self.set_up_relay((addr.addr, addr.port))
        if ret:
            return True, (self.client.transport.get_extra_info('sockname'))
        else:
            return False, (None, None)

    async def connect_to_addr_udp(self, addr: Socks5AddrHeader):
        """
            In the reply to a UDP ASSOCIATE request, the BND.PORT and BND.ADDR
            fields indicate the port number/address where the client MUST send
            UDP request messages to be relayed.
        """
        return True, ('127.0.0.1', 1080)

    def data_received(self, data):
        if self.sock5_processor.get_state() in [constants.STAGE_SOCKS5_METHOD_SELECT,
                                                constants.STAGE_SOCKS5_METHOD_AUTHENTICATION,
                                                constants.STAGE_SOCKS5_REQUEST]:
            self.sock5_processor.do_request(data)
        elif self.sock5_processor.get_state() == constants.STAGE_SOCKS5_TCP_RELAY:
            asyncio.ensure_future(self.send_data_to_remote(self.client, data), loop=self.loop)
        elif self.sock5_processor.get_state() == constants.SOCKS_SERVER_MODE_UDP_RELAY:
            # never goto here
            self.transport.close()


if __name__ == '__main__':
    pass
