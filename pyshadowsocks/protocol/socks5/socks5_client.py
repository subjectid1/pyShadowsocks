#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
from typing import Callable

import constants
import settings
from constants import STAGE_SOCKS5_METHOD_SELECT, STAGE_SOCKS5_TCP_RELAY, STRUCT_BBB, SOCKS5_VERSION, \
    SOCKS5_METHOD_NO_AUTHENTICATION_REQUIRED, STAGE_SOCKS5_REQUEST
from protocol.COMMON.base_protocal import BaseProtocol
from protocol.socks5.header import Socks5AddrHeader
from util.net.address import what_type_of_the_address


class SOCKS5ConnectProtocol(BaseProtocol):
    """Use for Testing the socks5_server"""

    def __init__(self, loop, target_host, target_port,
                 connected_callback: Callable[[BaseProtocol], None],
                 data_callback: Callable[[bytes], None]):

        super(SOCKS5ConnectProtocol, self).__init__()
        self.loop = loop

        self.data_buffer = b''
        self.connected_callback = connected_callback
        self.data_callback = data_callback
        self.target_host = target_host

        self.target_port = target_port

        self.state = STAGE_SOCKS5_METHOD_SELECT

    def start(self):
        self._send_socks5_method_select_request()

    def send_stream(self, data: bytes):
        if self.state == STAGE_SOCKS5_TCP_RELAY:
            data = self.data_buffer + data
            self.data_buffer = b''
            return self.transport.write(data)
        else:
            self.data_buffer += data

    def _send_socks5_method_select_request(self):
        #
        # request:
        # +-----+----------+----------+
        # | VER | NMETHODS | METHODS  |
        # +-----+----------+----------+
        # | 1   | 1        |   1to255 |
        # +-----+----------+----------+
        #
        data = STRUCT_BBB.pack(SOCKS5_VERSION, 1, SOCKS5_METHOD_NO_AUTHENTICATION_REQUIRED)
        self.transport.write(data)
        return True

    def _do_socks5_method_select_response(self, data):
        #
        # response:
        # +-----+--------+
        # | VER | METHOD |
        # +-----+--------+
        # | 1   | 1      |
        # +-----+--------+
        #
        if len(data) < constants.STRUCT_BB.size:
            settings.PROTO_LOG.error(constants.ERROR_MSG_NOT_ENOUGHT_DATA_FOR.format('socks5 method select response'))
            self.transport.close()

        version, method = constants.STRUCT_BB.unpack_from(data)
        if method == constants.SOCKS5_METHOD_NO_AUTHENTICATION_REQUIRED:
            return True
        elif method == constants.SOCKS5_METHOD_NO_ACCEPTABLE_METHODS:
            # If the selected METHOD is X'FF', none of the methods listed by the
            # client are acceptable, and the client MUST close the connection.
            self.transport.close()
            return False

    def _send_socks5_connect_request(self):
        #
        # resquest:
        # +-----+-----+-------+------+----------+----------+
        # | VER | CMD | RSV   | ATYP | DST.ADDR | DST.PORT |
        # +-----+-----+-------+------+----------+----------+
        # | 1   | 1   | X'00' | 1    | Variable | 2        |
        # +-----+-----+-------+------+----------+----------+
        #
        addr = Socks5AddrHeader()
        addr.addr = self.target_host
        addr.port = self.target_port
        addr.addr_type = what_type_of_the_address(self.target_host)

        data = STRUCT_BBB.pack(constants.SOCKS5_VERSION,
                               constants.SOCKS5_CMD_CONNECT,
                               constants.SOCKS5_RESERVED_BYTE,
                               ) + addr.to_bytes()

        self.transport.write(data)
        return True

    def _do_socks5_connect_response(self, data):
        # response:
        # +-----+-----+-------+------+----------+----------+
        # | VER | REP | RSV   | ATYP | BND.ADDR | BND.PORT |
        # +-----+-----+-------+------+----------+----------+
        # | 1   | 1   | X'00' | 1    | Variable | 2        |
        # +-----+-----+-------+------+----------+----------+
        #
        if len(data) < 10:
            settings.PROTO_LOG.error(constants.ERROR_MSG_NOT_ENOUGHT_DATA_FOR.format('socks5 method connect response'))
            self.transport.close()
            return False

        version, reply_code, _ = STRUCT_BBB.unpack_from(data)
        if reply_code == constants.SOCKS5_REPLY_SUCCEEDED:
            try:
                addr = Socks5AddrHeader()
                length = addr.from_bytes(data[STRUCT_BBB.size:])
                return True
            except ValueError:
                settings.PROTO_LOG.exception('Fail to parse addr')
                self.transport.close()
                return False
        else:
            # When a reply (REP value other than X'00') indicates a failure, the
            # SOCKS server MUST terminate the TCP connection shortly after sending
            # the reply. Here we close the client too.
            settings.PROTO_LOG.error('error code for connect response:%d', reply_code)
            self.transport.close()
            return False

    def data_received(self, data):
        if self.state == STAGE_SOCKS5_METHOD_SELECT:
            ret = self._do_socks5_method_select_response(data)
            if ret:
                self._send_socks5_connect_request()
                self.state = STAGE_SOCKS5_REQUEST

        elif self.state == STAGE_SOCKS5_REQUEST:
            ret = self._do_socks5_connect_response(data)
            if ret:
                self.state = STAGE_SOCKS5_TCP_RELAY
                self.connected_callback(self)

        elif self.state == STAGE_SOCKS5_TCP_RELAY:
            self.data_callback(data)
