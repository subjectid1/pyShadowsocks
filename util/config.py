#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
#
# Info:
#
import argparse
import configparser

import os.path
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


def parse_args(args=None):
    parser = argparse.ArgumentParser(description='This program implement the shadowsocks protocol.')
    parser.add_argument('--protocol', dest='protocol', required=True, default='shadowsocks', help='proxy solusion.')
    parser.add_argument('--password', dest='password', required=False, help='proxy solusion.')
    parser.add_argument('--cipher_method', dest='cipher_method', required=False, help='proxy solusion.')
    parser.add_argument('--ota_enabled', dest='ota_enabled', required=False, default=False, help='proxy solusion.')

    # group = parser.add_mutually_exclusive_group(required=True)

    args = parser.parse_args(args=args)
    return vars(args)
