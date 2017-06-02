#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
import struct

import encrypt

ONETIMEAUTH_BYTES = 10
ONETIMEAUTH_CHUNK_BYTES = 12
ONETIMEAUTH_CHUNK_DATA_LEN = 2

RELAY_CONNECT_TIMEOUT = 10

ADDRTYPE_AUTH = 0x10
ADDRTYPE_MASK = 0xF

TCP_BUF_SIZE = 1024 * 32

## for server relay state
RELAY_STATE_NOT_CONNECTED = 'not connected'
RELAY_STATE_CONNECTING = 'connecting'
RELAY_STATE_CONECTED = 'connected'

########################## FOR SOCKS5 #######################
SOCKS5_VERSION = 0x05
SOCKS5_METHOD_NO_AUTHENTICATION_REQUIRED = 0x00
SOCKS5_METHOD_GSSAPI = 0x01
SOCKS5_METHOD_USERNAME_PASSWORD = 0x02
SOCKS5_METHOD_NO_ACCEPTABLE_METHODS = 0xFF

# SOCKS command definition
SOCKS5_CMD_CONNECT = 0x01
SOCKS5_CMD_BIND = 0x02
SOCKS5_CMD_UDP_ASSOCIATE = 0x03

SOCKS5_REPLY_SUCCEEDED = 0x00
SOCKS5_REPLY_GENERAL_SOCKS_SERVER_FAILURE = 0x01
SOCKS5_REPLY_CONNECTION_NOT_ALLOWED_BY_RULESET = 0x02
SOCKS5_REPLY_NETWORK_UNREACHABLE = 0x03
SOCKS5_REPLY_HOST_UNREACHABLE = 0x04
SOCKS5_REPLY_CONNECTION_REFUSED = 0x05
SOCKS5_REPLY_TTL_EXPIRED = 0x06
SOCKS5_REPLY_COMMAND_NOT_SUPPORTED = 0x07
SOCKS_REPLY_ADDRESS_TYPE_NOT_SUPPORTED = 0x08

SOCKS5_RESERVED_BYTE = 0x00

# use the value defined by SOCKS5 protocol
SOCKS5_ADDRTYPE_IPV4 = 0x01
SOCKS5_ADDRTYPE_IPV6 = 0x04
SOCKS5_ADDRTYPE_HOST = 0x03

STAGE_SOCKS5_METHOD_SELECT = 0
STAGE_SOCKS5_USERNAME_PASSWORD_AUTHENTICATION = 1
STAGE_SOCKS5_REQUEST = 2
STAGE_SOCKS5_UDP_ASSOCIATE = 5
STAGE_SOCKS5_TCP_RELAY = 6
STAGE_DESTROYED = -1

##################################################################

STRUCT_BBB = struct.Struct('>BBB')
STRUCT_BB = struct.Struct('>BB')
STRUCT_B = struct.Struct('>B')
STRUCT_SOCK5_REQUEST = struct.Struct('>BBBBIH')
STRUCT_SOCK5_REPLY = STRUCT_SOCK5_REQUEST

ERROR_MSG_NOT_ENOUGHT_DATA_FOR = 'not enought data for {}'

PROTOCOL_SHADOWSOCKS = 'shadowsocks'

#############################For argument parsing #######################################
### args for server
ARG_SERVER_MODE = 'server_mode'
ARG_LOCAL_SERVER = 'local'
ARG_REMOTE_SERVER = 'remote'

ARG_SOCKS_LISTEN_PORT = 'socks_port'
ARG_PAC_LISTEN_PORT = 'pac_port'

ARG_LISTEN_PORT = 'listen_port'
ARG_REMOTE_HOST = 'remote_host'
ARG_REMOTE_PORT = 'remote_port'

### args for protocal
ARG_PROTOCOL_MODE = 'protocol_mode'
ARG_PROTOCOL_SHADOWSOCKS = PROTOCOL_SHADOWSOCKS

ARG_USERNAME = 'user'
ARG_PASSWORD = 'password'
ARG_CIPHER_METHOD = 'cipher_method'
ARG_OTA_ENABLED = 'ota_enabled'

SERVER_MODES = [
    ARG_LOCAL_SERVER,
    ARG_REMOTE_SERVER,
]

PROTOCOL_MODES = [
    ARG_PROTOCOL_SHADOWSOCKS,
]

### argparse.parser.add_parser arguments for modes
ARUMENTS_FOR_ADD_PARSER = {
    ARG_LOCAL_SERVER: {
        ARG_REMOTE_HOST: {'required': True},
        ARG_REMOTE_PORT: {'type': int, 'required': True},
        ARG_SOCKS_LISTEN_PORT: {'type': int, 'required': False, 'default': 1080},
        ARG_PAC_LISTEN_PORT: {'type': str, 'required': False, 'default': None},
    },
    ARG_REMOTE_SERVER: {
        ARG_LISTEN_PORT: {'type': int, 'required': True},
    },
    ARG_PROTOCOL_SHADOWSOCKS: {
        ARG_PASSWORD: {'required': True},
        ARG_CIPHER_METHOD: {'choices': encrypt.SymmetricEncryptions, 'required': True},
        ARG_OTA_ENABLED: {'required': False, 'default': False},
    },

}
