#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
#
from abc import abstractmethod, ABCMeta

from util.collections.fixed_dict import FixedDict


class PacketHeader(FixedDict, metaclass=ABCMeta):
    @abstractmethod
    def to_bytes(self):
        pass

    @abstractmethod
    def from_bytes(self, data):
        pass
