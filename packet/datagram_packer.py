#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
from abc import abstractmethod


class DatagramPacker(object):
    def __init__(self, mode):
        pass

    @abstractmethod
    def pack(self, header=None, data=None):
        pass

    @abstractmethod
    def unpack(self, data):
        """return header and raw data"""
        pass