#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
#
import abc
from util import FixedDict


class PacketHeader(FixedDict, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def to_bytes(self):
        pass

    @abc.abstractmethod
    def from_bytes(self, data):
        pass
