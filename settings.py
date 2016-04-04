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

PROTO_LOG = get_logger('protocal', logging.INFO)
CONFIG_LOG = get_logger('config', logging.INFO)
CONFIG_FILES = ['/etc/pyshadowsocks.ini', '~/.pyshadowsocks.ini', './pyshadowsocks.ini']

protocal = 'shadowsocks'
password = 'O3O4O5O6'
cipher_method = 'aes-256-cfb'
ota_enabled = False
