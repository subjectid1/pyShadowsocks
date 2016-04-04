#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
#
# Info:
#
import argparse
import configparser

import constants
import encrypt
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


def parse_args(is_local=True, args=None):
    parser = argparse.ArgumentParser(description='This program implement the shadowsocks protocol.')
    if is_local:
        parser.add_argument('--remote_host', dest='remote_host', required=True, help='remote host')
        parser.add_argument('--remote_port', dest='remote_port', type=int, required=True, help='remote port')
        parser.add_argument('--listen_port', dest='listen_port', required=False, type=int, default=1080,
                            help='local port')
    else:
        parser.add_argument('--listen_port', dest='listen_port', required=True, type=int, help='local port')

    parser.add_argument('--protocol', dest='protocol', required=True, default=constants.PROTOCOL_SHADOWSOCKS,
                        choices=[constants.PROTOCOL_SHADOWSOCKS], help='proxy solusion.')
    parser.add_argument('--password', dest='password', required=True)
    parser.add_argument('--cipher_method', dest='cipher_method', choices=encrypt.SymmetricEncryptions,
                        required=True)
    parser.add_argument('--ota_enabled', dest='ota_enabled', required=False, default=False)

    args = parser.parse_args(args=args)
    return vars(args)
