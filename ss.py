#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: 
# 
# Info:
#
#
import settings
from util.config import parse_args

if __name__ == '__main__':
    for key, value in parse_args():
        setattr(settings, key, value)
