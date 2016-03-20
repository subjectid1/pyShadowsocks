#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
from abc import abstractmethod
from typing import Dict

class Header(Dict):
    ValidFields = []

    def __setitem__(self, key, value):
        if key in self.ValidFields:
            return super(Header, self).__setitem__(key, value)
        else:
            raise KeyError

    def __getitem__(self, item):
        try:
            return super(Header, self).__getitem__(item)
        except KeyError:
            if item in self.ValidFields:
                return None
            else:
                raise

    def __setattr__(self, key, value):
        return self.__setitem__(key, value)

    def __getattr__(self, item):
        return self.__getitem__(item)

    @abstractmethod
    def to_bytes(self):
        pass

    @abstractmethod
    def from_bytes(self, data):
        pass

