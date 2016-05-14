#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
#
# Info:
#
#
import asyncio
from typing import Callable, Tuple

import constants
import settings
from constants import STAGE_SOCKS5_METHOD_SELECT, STAGE_SOCKS5_REQUEST, STAGE_SOCKS5_UDP_ASSOCIATE, \
    STAGE_SOCKS5_TCP_RELAY, \
    STRUCT_BBB, STRUCT_BB, STRUCT_B, STRUCT_SOCK5_REPLY
from protocol.socks5.header import Socks5AddrHeader
from util.net.address import what_type_of_the_address


class Socks5Processor(object):
    def __init__(self, loop, transport,
                 tcp_connect_coroutine: Callable[[Socks5AddrHeader], Tuple[str, int]],
                 udp_connect_coroutine: Callable[[Socks5AddrHeader], Tuple[str, int]]):
        self.loop = loop
        self.transport = transport

        # for socks5 connect request
        self._tcp_session_target_addr = None
        self._udp_connected_addr = None

        self.tcp_connect_coroutine = tcp_connect_coroutine
        self.udp_connect_coroutine = udp_connect_coroutine

        self.state = STAGE_SOCKS5_METHOD_SELECT

    @property
    def tcp_session_target_addr(self):
        if self.state == STAGE_SOCKS5_TCP_RELAY and self._tcp_session_target_addr:
            return self._tcp_session_target_addr
        return None

    def get_state(self):
        return self.state

    def do_request(self, data):
        if self.state == STAGE_SOCKS5_METHOD_SELECT:
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

            if constants.SOCKS5_METHOD_NO_AUTHENTICATION_REQUIRED in methods:
                # The server selects from one of the methods given in METHODS, and sends a METHOD selection message
                response_data = STRUCT_BB.pack(constants.SOCKS5_VERSION,
                                               constants.SOCKS5_METHOD_NO_AUTHENTICATION_REQUIRED)
                self.state = STAGE_SOCKS5_REQUEST
                self.transport.write(response_data)
                return True
            else:
                # If the selected METHOD is X'FF', none of the methods listed by the
                # client are acceptable, and the client MUST close the connection.
                #
                response_data = STRUCT_BB.pack(constants.SOCKS5_VERSION, constants.SOCKS5_METHOD_NO_ACCEPTABLE_METHODS)
                self.transport.write(response_data)
                return False

        elif self.state == STAGE_SOCKS5_REQUEST:
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
                    self._tcp_session_target_addr = addr
                    f = asyncio.ensure_future(self.tcp_connect_coroutine(self._tcp_session_target_addr), loop=self.loop)

                elif cmd == constants.SOCKS5_CMD_UDP_ASSOCIATE:
                    self._udp_connected_addr = addr
                    f = asyncio.ensure_future(self.udp_connect_coroutine(self._udp_connected_addr), loop=self.loop)

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
