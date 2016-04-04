#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
import logging

from util.log import get_logger

PROTO_LOG = get_logger('protocol', logging.INFO)
CONFIG_LOG = get_logger('config', logging.INFO)
CONFIG_FILES = ['/etc/pyshadowsocks.ini', '~/.pyshadowsocks.ini', './pyshadowsocks.ini']

# [local]
remote_host = None
remote_port = None

# [remote]
listen_port = None

# [protocol]
protocol = None

# [shadowsocks]
password = None
cipher_method = None
ota_enabled = False
