#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
import logging

import constants
from util.log import get_logger

PROTO_LOG = get_logger('protocol', logging.WARN)
CONFIG_LOG = get_logger('config', logging.INFO)
CONFIG_FILES = ['/etc/pyshadowsocks.ini', '~/.pyshadowsocks.ini', './pyshadowsocks.ini']
