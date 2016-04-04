#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#

from protocal.socks5.header import Socks5AddrHeader


class ShadowsocksPacketHeader(Socks5AddrHeader):
    ValidFields = ['addr_type', 'addr', 'port', 'sha1_hmac']

    def to_bytes(self):
        data = super(ShadowsocksPacketHeader, self).to_bytes()
        sha1_hmac = self.sha1_hmac or b''
        return data + sha1_hmac
