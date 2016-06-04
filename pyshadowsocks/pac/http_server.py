#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
import os.path
from protocol.COMMON.base_protocal import BaseProtocol


class FakePACGetProtocol(BaseProtocol):
    def data_received(self, data):
        # GET /proxy.pac HTTP/1.1\r\n
        if data.startswith(b'GET /proxy.pac'):
            header = 'HTTP/1.1 200 OK\r\nContent-Length={}\r\nContent-Type:application/x-ns-proxy-autoconfig\r\nConnection:Close\r\n\r\n'
            file_data = open(os.path.join(os.path.dirname(__file__), 'proxy.pac'), 'rb').read()
            header = header.format(len(file_data)).encode('utf-8')
            self.transport.write(header + file_data)
            self.transport.close()
