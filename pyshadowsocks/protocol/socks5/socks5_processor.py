#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
#
# Info:
#
#
import asyncio
from typing import Callable, Tuple, Dict

import constants
import settings
from constants import STAGE_SOCKS5_UDP_ASSOCIATE, \
    STAGE_SOCKS5_TCP_RELAY, \
    STRUCT_BBB, STRUCT_BB, STRUCT_B, STRUCT_SOCK5_REPLY
from protocol.socks5.header import Socks5AddrHeader
from util.net.address import what_type_of_the_address


class Socks5Processor(object):
    def __init__(self, loop, transport,
                 tcp_connect_coroutine: Callable[[Socks5AddrHeader], Tuple[str, int]],
                 udp_connect_coroutine: Callable[[Socks5AddrHeader], Tuple[str, int]],
                 auth=constants.SOCKS5_METHOD_NO_AUTHENTICATION_REQUIRED,
                 username_passwords: Dict = None):

        self.loop = loop
        self.transport = transport

        self.tcp_connect_coroutine = tcp_connect_coroutine
        self.udp_connect_coroutine = udp_connect_coroutine

        self.auth = auth
        self.username_passwords = username_passwords

        self.state = constants.STAGE_SOCKS5_METHOD_SELECT

    def upd_relaying(self):
        return self.state == constants.STAGE_SOCKS5_UDP_ASSOCIATE

    def tcp_relaying(self):
        return self.state == constants.STAGE_SOCKS5_TCP_RELAY

    def neek_more_data(self):
        return self.state not in [constants.STAGE_SOCKS5_TCP_RELAY, constants.STAGE_SOCKS5_UDP_ASSOCIATE]

    def feed_data(self, data):
        if self.state == constants.STAGE_SOCKS5_METHOD_SELECT:
            #
            # request:
            # +-----+----------+----------+
            # | VER | NMETHODS | METHODS  |
            # +-----+----------+----------+
            # | 1   | 1        |   1to255 |
            # +-----+----------+----------+
            #
            # response:
            # +-----+--------+
            # | VER | METHOD |
            # +-----+--------+
            # | 1   | 1      |
            # +-----+--------+
            #
            if len(data) < 3:
                settings.PROTO_LOG.warn('no enough data for SOCKS METHOD SELECT')
                self.transport.close()
                return False

            version, num_of_methods = STRUCT_BB.unpack_from(data)
            method_data = data[STRUCT_BB.size:]
            method_data = method_data[:num_of_methods]
            methods = [method for method, in STRUCT_B.iter_unpack(method_data)]

            if self.auth in methods:
                # The server selects from one of the methods given in METHODS, and sends a METHOD selection message
                response_data = STRUCT_BB.pack(constants.SOCKS5_VERSION, self.auth)

                if self.auth == constants.SOCKS5_METHOD_NO_AUTHENTICATION_REQUIRED:
                    self.state = constants.STAGE_SOCKS5_REQUEST
                elif self.auth == constants.SOCKS5_METHOD_USERNAME_PASSWORD:
                    self.state = constants.STAGE_SOCKS5_USERNAME_PASSWORD_AUTHENTICATION

                self.transport.write(response_data)
                return True
            else:
                # If the selected METHOD is X'FF', none of the methods listed by the
                # client are acceptable, and the client MUST close the connection.
                #
                response_data = STRUCT_BB.pack(constants.SOCKS5_VERSION, constants.SOCKS5_METHOD_NO_ACCEPTABLE_METHODS)
                self.transport.write(response_data)
                return False

        elif self.state == constants.STAGE_SOCKS5_USERNAME_PASSWORD_AUTHENTICATION:
            #
            # +----+------+----------+------+----------+
            # |VER | ULEN | UNAME    | PLEN | PASSWD   |
            # +----+------+----------+------+----------+
            # | 1  | 1    | 1 to 255 | 1    | 1 to255  |
            # +----+------+----------+------+----------+
            #
            version, len_of_user = STRUCT_BB.unpack_from(data)
            data = data[STRUCT_BB.size:]

            user = data[:len_of_user].decode('utf-8')
            data = data[len_of_user:]

            len_of_password, = STRUCT_B.unpack_from(data[:1])
            data = data[1:]
            password = data[:len_of_password].decode('utf-8')

            # +----+--------+
            # |VER | STATUS |
            # +----+--------+
            # | 1  | 1      |
            # +----+--------+
            #
            # A STATUS field of X'00' indicates success. If the server returns a
            # `failure' (STATUS value other than X'00') status, it MUST close the
            # connection.
            #
            if user in self.username_passwords and self.username_passwords[user] == password:
                self.state = constants.STAGE_SOCKS5_REQUEST
                # The VER field contains the current version of the subnegotiation,
                # which is X'01'.
                self.transport.write(STRUCT_BB.pack(0x01, 0))
                return True
            else:
                self.transport.write(STRUCT_BB.pack(0x01, 0xFF))
                self.transport.close()
                return False

        elif self.state == constants.STAGE_SOCKS5_REQUEST:
            #
            # resquest:
            # +-----+-----+-------+------+----------+----------+
            # | VER | CMD | RSV   | ATYP | DST.ADDR | DST.PORT |
            # +-----+-----+-------+------+----------+----------+
            # | 1   | 1   | X'00' | 1    | Variable | 2        |
            # +-----+-----+-------+------+----------+----------+
            #
            # response:
            # +-----+-----+-------+------+----------+----------+
            # | VER | REP | RSV   | ATYP | BND.ADDR | BND.PORT |
            # +-----+-----+-------+------+----------+----------+
            # | 1   | 1   | X'00' | 1    | Variable | 2        |
            # +-----+-----+-------+------+----------+----------+
            #

            ret, cmd, addr = self._parse_socks_request(data)

            if not ret:
                return False
            elif not cmd in [constants.SOCKS5_CMD_CONNECT, constants.SOCKS5_CMD_UDP_ASSOCIATE]:
                self._write_error_socks_response_with_reply_code(constants.SOCKS5_REPLY_COMMAND_NOT_SUPPORTED)
                return False
            else:
                f = None
                if cmd == constants.SOCKS5_CMD_CONNECT:
                    f = asyncio.ensure_future(self.tcp_connect_coroutine(addr), loop=self.loop)

                elif cmd == constants.SOCKS5_CMD_UDP_ASSOCIATE:
                    f = asyncio.ensure_future(self.udp_connect_coroutine(addr), loop=self.loop)

                def conn_completed(future):
                    # socks5 states: In the reply to a CONNECT, BND.PORT contains the port number that
                    # the server assigned to connect to the target host, while BND.ADDR contains the associated IP address.
                    ret, (foward_addr, foward_port) = future.result()
                    if not ret:
                        self._write_error_socks_response_with_reply_code(constants.SOCKS5_REPLY_NETWORK_UNREACHABLE)
                        return False
                    else:
                        # If the reply code (REP value of X'00') indicates a success,
                        # and the request was either a BIND or a CONNECT, the client may now start passing data.
                        self._write_succeed_socks_response_with_addr(Socks5AddrHeader(
                            addr=foward_addr,
                            port=foward_port,
                            addr_type=what_type_of_the_address(foward_addr),
                        ))

                        if cmd == constants.SOCKS5_CMD_CONNECT:
                            self.state = STAGE_SOCKS5_TCP_RELAY
                        elif cmd == constants.SOCKS5_CMD_UDP_ASSOCIATE:
                            self.state = STAGE_SOCKS5_UDP_ASSOCIATE
                            # close the connection and go to the UDP relay server for data relay
                            self.transport.close()

                f.add_done_callback(conn_completed)
                return True

    def _write_error_socks_response_with_reply_code(self, reply_code):
        response_data = STRUCT_SOCK5_REPLY.pack(constants.SOCKS5_VERSION,
                                                reply_code,
                                                constants.SOCKS5_RESERVED_BYTE,
                                                constants.SOCKS5_ADDRTYPE_IPV4,
                                                0,
                                                0,
                                                )

        self.transport.write(response_data)
        self.transport.close()

    def _write_succeed_socks_response_with_addr(self, addr):
        response_data = STRUCT_BBB.pack(constants.SOCKS5_VERSION,
                                        constants.SOCKS5_REPLY_SUCCEEDED,
                                        constants.SOCKS5_RESERVED_BYTE,
                                        ) + addr.to_bytes()

        self.transport.write(response_data)

    def _parse_socks_request(self, data):
        """
        return the CMD and address(extract from DST.addr DST.port),
        if ERROR, close the transport and return (False, None, None)
        """

        if len(data) < 10:
            settings.PROTO_LOG.error('no enough data for SOCKS request')
            self.transport.close()
            return False

        version, cmd, _ = STRUCT_BBB.unpack_from(data)
        addr = Socks5AddrHeader()

        try:
            length = addr.from_bytes(data[STRUCT_BBB.size:])
        except ValueError:
            settings.PROTO_LOG.exception('Fail to get addr')
            self._write_error_socks_response_with_reply_code(constants.SOCKS_REPLY_ADDRESS_TYPE_NOT_SUPPORTED)
            return False, None, None
        else:
            return True, cmd, addr
