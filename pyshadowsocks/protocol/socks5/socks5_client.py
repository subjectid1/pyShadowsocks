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
    STAGE_SOCKS5_REQUEST
from protocol.COMMON.base_protocal import BaseProtocol
from protocol.socks5.header import Socks5AddrHeader
from util.net.address import what_type_of_the_address


class SOCKS5ConnectProtocol(BaseProtocol):
    """Use for Testing the socks5_server"""

    def __init__(self, loop,
                 target_host, target_port,
                 connected_callback: Callable[[BaseProtocol], None],
                 data_callback: Callable[[bytes], None],
                 user=None,
                 password=None):

        super(SOCKS5ConnectProtocol, self).__init__()
        self.loop = loop

        self.data_buffer = b''
        self.connected_callback = connected_callback
        self.data_callback = data_callback
        self.target_host = target_host
        self.target_port = target_port

        self.user = user
        self.password = password
        self.auth_method = ((self.user and self.password) and constants.SOCKS5_METHOD_NO_AUTHENTICATION_REQUIRED or
                            constants.SOCKS5_METHOD_USERNAME_PASSWORD)

        self.state = STAGE_SOCKS5_METHOD_SELECT

    def connection_made(self, transport):
        super(SOCKS5ConnectProtocol, self).connection_made(transport)
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

        data = STRUCT_BBB.pack(SOCKS5_VERSION, 1, self.auth_method)
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

        if method == constants.SOCKS5_METHOD_NO_ACCEPTABLE_METHODS:
            # If the selected METHOD is X'FF', none of the methods listed by the
            # client are acceptable, and the client MUST close the connection.
            self.transport.close()

        return method

    def _sent_socks5_username_password_authentication(self):

        #
        # +----+------+----------+------+----------+
        # |VER | ULEN | UNAME    | PLEN | PASSWD   |
        # +----+------+----------+------+----------+
        # | 1  | 1    | 1 to 255 | 1    | 1 to255  |
        # +----+------+----------+------+----------+
        #
        data = (constants.STRUCT_BB.pack(constants.SOCKS5_VERSION, len(self.user)) +
                self.user.encode('utf-8') +
                constants.STRUCT_B.pack(len(self.password)) +
                self.password.encode('utf-8'))
        self.transport.write(data)

    def _do_socks5_username_password_authentication(self, data):
        _, reply_code = constants.STRUCT_BB.unpack_from(data)
        return reply_code == 0x00


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
        if self.state == constants.STAGE_SOCKS5_METHOD_SELECT:
            method = self._do_socks5_method_select_response(data)
            if method == constants.SOCKS5_METHOD_NO_AUTHENTICATION_REQUIRED:
                self._send_socks5_connect_request()
                self.state = constants.STAGE_SOCKS5_REQUEST

            elif method == constants.SOCKS5_METHOD_USERNAME_PASSWORD:
                self._sent_socks5_username_password_authentication()
                self.state = constants.STAGE_SOCKS5_USERNAME_PASSWORD_AUTHENTICATION

        elif self.state == constants.STAGE_SOCKS5_USERNAME_PASSWORD_AUTHENTICATION:
            ret = self._do_socks5_username_password_authentication(data)
            if ret:
                self._send_socks5_connect_request()
                self.state = STAGE_SOCKS5_REQUEST

        elif self.state == constants.STAGE_SOCKS5_REQUEST:
            ret = self._do_socks5_connect_response(data)
            if ret:
                self.state = constants.STAGE_SOCKS5_TCP_RELAY
                self.connected_callback(self)

        elif self.state == constants.STAGE_SOCKS5_TCP_RELAY:
            self.data_callback(data)
