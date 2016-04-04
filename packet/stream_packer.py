#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
from encrypt.base.data_encoder import DataEncoder
from packet.packet_header import PacketHeader


class StreamPacker(object):
    """used by stream protocal like TCP"""

    def __init__(self):
        # counter bytes for later use
        self.in_bytes = 0
        self.out_bytes = 0

        # used for unpack mode
        self.data_buffer = b''

    def pack(self, header:PacketHeader=None, data=None):
        """return encode or compress data"""
        encoded_data = b''
        if header:
            encoded_data += header.to_bytes()

        if data:
            encoded_data += data

        if len(encoded_data) > 0:
            self.in_bytes += len(encoded_data)


        self.out_bytes += len(encoded_data)
        return encoded_data

    def unpack(self, header:PacketHeader=None, data=None):
        """return header and raw content"""
        self.in_bytes += len(data)

        if header is not None:
            all_data = self.data_buffer + data
            try:
                header_length = header.from_bytes(all_data)
            except ValueError:
                # need more data
                self.data_buffer = all_data
                return None, None
            except Exception as ex:
                # TODO:do something
                return None, None
            else:
                self.data_buffer = b''
                out_data = all_data[header_length:]
                self.out_bytes += len(all_data)
                return header, out_data
        else:
            out_data = self.data_buffer+data
            self.out_bytes += len(out_data)
            return None, out_data


