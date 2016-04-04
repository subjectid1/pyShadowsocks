#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
#
# Info:
#

import os.path
import sys
import configparser

import settings


def get_config():
    for config_file in settings.CONFIG_FILES:
        config_file = os.path.abspath(os.path.expanduser(config_file))

        if os.path.exists(config_file):
            config = configparser.ConfigParser()
            if os.path.exists(config_file):
                try:
                    config.read(config_file)
                    return config
                except:
                    settings.CONFIG_LOG.exception("Config file format error! (%s)", config_file)
                    return None

    return None


def get_config_by_section(section):
    config = get_config()
    return config[section]

