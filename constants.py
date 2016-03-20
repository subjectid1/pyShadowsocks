#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#

ONETIMEAUTH_BYTES = 10
ONETIMEAUTH_CHUNK_BYTES = 12
ONETIMEAUTH_CHUNK_DATA_LEN = 2

# SOCKS command definition
CMD_CONNECT = 1
CMD_BIND = 2
CMD_UDP_ASSOCIATE = 3

#use the value defined by SOCKS5 protocal
ADDRTYPE_IPV4 = 0x01
ADDRTYPE_IPV6 = 0x04
ADDRTYPE_HOST = 0x03

ADDRTYPE_AUTH = 0x10
ADDRTYPE_MASK = 0xF

