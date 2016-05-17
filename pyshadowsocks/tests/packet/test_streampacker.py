#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
import unittest


import os
from encrypt.base.data_encoder import DataEncoder
from packet.packet_header import PacketHeader
from packet.stream_packer import StreamPacker


class DummyPacketHeader(PacketHeader):
    ValidFields = ['one_byte']

    def from_bytes(self, data):
        self.one_byte = data[:1]
        return 1

    def to_bytes(self):
        if self.one_byte:
            return self.one_byte
        else:
            return b''


class DummyEncoder(DataEncoder):

    def encode(self, data, end=False):
        return data

    def decode(self, data, end=False):
        return data

class StreamPackerTest(unittest.TestCase):
    def test_StreamPacker_pack_and_unpack(self):
        packer = StreamPacker()
        unpacker = StreamPacker()

        data_header = b'X'
        data1 = os.urandom(30)
        data2 = os.urandom(20)

        dummy_header = DummyPacketHeader()
        dummy_header.from_bytes(data_header)

        encoded_data = packer.pack(dummy_header, data1)
        encoded_data += packer.pack(None, data2)

        header, decoded_data = unpacker.unpack(encoded_data, DummyPacketHeader())
        self.assertEqual(header.to_bytes() + decoded_data, data_header + data1 + data2)

        in_bytes_1 = packer.in_bytes
        in_bytes_2 = unpacker.in_bytes
        out_bytes_1 = packer.out_bytes
        out_bytes_2 = packer.out_bytes
        self.assertEqual(in_bytes_1, out_bytes_2)
        self.assertEqual(out_bytes_1, in_bytes_2)

        # TODO:
        # 1. end=True的怎么处理？
