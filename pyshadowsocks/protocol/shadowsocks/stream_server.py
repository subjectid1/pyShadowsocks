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
import settings
from packet.stream_packer import StreamPacker
from protocol.COMMON.server_stream_relay_protocol import ServerStreamRelayProtocol
from protocol.shadowsocks.encoder import ShadowsocksEncryptionWrapperEncoder
from protocol.shadowsocks.header import ShadowsocksPacketHeader


class ShadowsocksServerStreamRelayProtocol(ServerStreamRelayProtocol):
    def __init__(self, loop, config: Namespace = None):
        super(ShadowsocksServerStreamRelayProtocol, self).__init__(loop, config)
        self.relay_target_addr = None
        self.stream_packer = StreamPacker()

        self.relay_state = constants.RELAY_STATE_NOT_CONNECTED

    def create_encoder(self):
        return ShadowsocksEncryptionWrapperEncoder(
            encrypt_method=self.config.cipher_method,
            password=self.config.password,
            encript_mode=True)

    def create_decoder(self):
        return ShadowsocksEncryptionWrapperEncoder(
            encrypt_method=self.config.cipher_method,
            password=self.config.password,
            encript_mode=False)

    def data_received(self, data):
        if self.decoder:
            data = self.decoder.decode(data)

        if not self.relay_target_addr:
            try:
                self.relay_target_addr, data = self.stream_packer.unpack(data, header=ShadowsocksPacketHeader())
            except AttributeError:
                settings.PROTO_LOG.error('parsing header error from %s:%d', *self.transport.get_extra_info('peername'))
                self.transport.close()
            else:
                if not self.relay_target_addr:
                    # need more data to be a header
                    return

        else:
            _, data = self.stream_packer.unpack(data)
            if not data:
                return

        if self.relay_state == constants.RELAY_STATE_CONECTED:
            # TODO: inspect the relay client' connection status, try to reconnect if disconn
            asyncio.ensure_future(self.send_data_to_remote(self.client, data), loop=self.loop)

        elif self.relay_state == constants.RELAY_STATE_CONNECTING:
            settings.PROTO_LOG.error('unexpected state: receive data before connection completes')

        elif self.relay_state == constants.RELAY_STATE_NOT_CONNECTED:

            f = asyncio.ensure_future(self.set_up_relay(self.relay_target_addr.addr, self.relay_target_addr.port),
                                      loop=self.loop)
            self.relay_state = constants.RELAY_STATE_CONNECTING

            def send_data(future):
                succed = future.result()
                if succed:
                    self.relay_state = constants.RELAY_STATE_CONECTED
                    asyncio.ensure_future(self.send_data_to_remote(self.client, data), loop=self.loop)
                else:
                    self.relay_state = constants.RELAY_STATE_NOT_CONNECTED
                    settings.PROTO_LOG.warning('can not create relay connection to %s:%d',
                                               self.relay_target_addr.addr,
                                               self.relay_target_addr.port)
                    self.transport.close()

            f.add_done_callback(send_data)
