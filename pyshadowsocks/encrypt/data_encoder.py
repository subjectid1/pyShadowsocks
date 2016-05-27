#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
from abc import abstractmethod


class DataEncoder(object):

    @abstractmethod
    def encode(self, data, end=False):
        pass

    @abstractmethod
    def decode(self, data, end=False):
        pass