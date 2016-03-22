#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
from encrypt.base.data_encoder import DataEncoder
from protocal.header import Header


class StreamPacker(object):
    """used by stream protocal like TCP"""

    def __init__(self, encoder: DataEncoder = None, header_type: Header = None):
        self.data_encoder = encoder
        self.header_type = header_type
        self.header = None

        # counter bytes for later use
        self.in_bytes = 0
        self.out_bytes = 0
        self.data_buffer = b''

    def pack(self, header=None, data=None):
        """return encode or compress data"""
        encoded_data = b''
        if header:
            self.header = header
            encoded_data += header.to_bytes()

        if data:
            encoded_data += data

        if len(encoded_data) > 0:
            self.in_bytes += len(encoded_data)

        if self.data_encoder:
            encoded_data = self.data_encoder.encode(encoded_data)

        self.out_bytes += len(encoded_data)
        return encoded_data

    def unpack(self, data=None, has_header=False):
        """return header and raw content"""
        self.in_bytes += len(data)
        raw_data = self.data_encoder.decode(data)

        if not self.header and has_header:
            header = self.header_type()
            try:
                all_data = self.data_buffer+raw_data
                header_length = header.from_bytes(all_data)
            except ValueError:
                # need more data
                self.data_buffer = all_data
                return
            except Exception as ex:
                # do something
                return
            else:
                self.data_buffer = b''
                self.header = header
                out_data = all_data[header_length:]
                self.out_bytes += len(all_data)
                return self.header, out_data
        else:
            out_data = self.data_buffer+raw_data
            self.out_bytes += len(out_data)
            return None, out_data


