#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
from typing import Dict


class FixedDict(Dict):
    ValidFields = []

    def __setitem__(self, key, value):
        if key in self.ValidFields:
            return super(FixedDict, self).__setitem__(key, value)
        else:
            raise KeyError

    def __getitem__(self, item):
        try:
            return super(FixedDict, self).__getitem__(item)
        except KeyError:
            if item in self.ValidFields:
                return None
            else:
                raise

    def __setattr__(self, key, value):
        return self.__setitem__(key, value)

    def __getattr__(self, item):
        return self.__getitem__(item)
