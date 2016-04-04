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

import config
import constants
from constants import STAGE_SOCKS5_METHOD_SELECT, STAGE_SOCKS5_REQUEST, STAGE_SOCKS5_UDP_ASSOCIATE, STAGE_RELAY, \
    STRUCT_BBB, STRUCT_BB, STRUCT_B, STRUCT_SOCK5_REPLY
from protocal.shadowsocks.header import Socks5AddrHeader
from util.address import what_type_of_the_address


class Socks5Processor(object):
    def __init__(self, loop, transport, connect_coroutine: Callable[[Socks5AddrHeader], Tuple[str, int]]):
        self.loop = loop
        self.transport = transport

        # for socks5 connect request
        self._connected_addr = None
        self.connect_coroutine = connect_coroutine

        self.state = STAGE_SOCKS5_METHOD_SELECT

    @property
    def connected_addr(self):
        if self.socks_connected() and self._connected_addr:
            return self._connected_addr
        return None

    def socks_connected(self):
        return self.state == STAGE_RELAY

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
                config.PROTO_LOG.warn('no enough data for SOCKS METHOD SELECT')
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
            if len(data) < 10:
                config.PROTO_LOG.error('no enough data for SOCKS request')
                self.transport.close()
                return False

            version, cmd, _ = STRUCT_BBB.unpack_from(data)
            if cmd == constants.SOCKS5_CMD_CONNECT:
                remain_data = data[STRUCT_BBB.size:]
                addr = Socks5AddrHeader()

                try:
                    length = addr.from_bytes(remain_data)
                except ValueError:
                    config.PROTO_LOG.exception('Fail to get addr')
                    response_data = STRUCT_SOCK5_REPLY.pack(constants.SOCKS5_VERSION,
                                                            constants.SOCKS_REPLY_ADDRESS_TYPE_NOT_SUPPORTED,
                                                            constants.SOCKS5_RESERVED_BYTE,
                                                            constants.SOCKS5_ADDRTYPE_IPV4,
                                                            0,
                                                            0,
                                                            )
                    self.transport.write(response_data)
                    self.transport.close()
                    return False

                self._connected_addr = addr
                f = asyncio.ensure_future(self.connect_coroutine(self._connected_addr), loop=self.loop)

                def conn_completed(future):
                    self.state = STAGE_RELAY
                    #
                    # socks5 states: In the reply to a CONNECT, BND.PORT contains the port number that
                    # the server assigned to connect to the target host, while BND.ADDR contains the associated IP address.
                    #
                    #
                    remote_addr, remote_port = future.result()
                    addr = Socks5AddrHeader()
                    addr.addr = remote_addr
                    addr.port = remote_port
                    # TODO: autoreconize the addr type
                    addr.addr_type = what_type_of_the_address(remote_addr)

                    response_data = STRUCT_BBB.pack(constants.SOCKS5_VERSION,
                                                    constants.SOCKS5_REPLY_SUCCEEDED,
                                                    constants.SOCKS5_RESERVED_BYTE,
                                                    ) + addr.to_bytes()

                    self.transport.write(response_data)

                f.add_done_callback(conn_completed)
                return True

            elif cmd == constants.SOCKS5_CMD_UDP_ASSOCIATE:
                # TODO
                pass
            else:
                config.PROTO_LOG.warn('cmd=>%d, socks5 dosnt support!', cmd)
                response_data = STRUCT_SOCK5_REPLY.pack(constants.SOCKS5_VERSION,
                                                        constants.SOCKS5_REPLY_COMMAND_NOT_SUPPORTED,
                                                        constants.SOCKS5_RESERVED_BYTE,
                                                        constants.SOCKS5_ADDRTYPE_IPV4,
                                                        0,
                                                        0,
                                                        )
                self.transport.write(response_data)
                self.transport.close()
                return False

        elif self.state == STAGE_SOCKS5_UDP_ASSOCIATE:
            #
            # socks5: If the reply code (REP value of X'00') indicates a success, and the
            # request was either a BIND or a CONNECT, the client may now sent_method_select_request passing data.
            #
            pass
