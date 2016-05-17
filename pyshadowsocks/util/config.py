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


def parse_args_new(args=None):
    def add_argument(parser, mode, arg):
        parser.add_argument('--' + arg, dest=arg, **constants.ARUMENTS_FOR_ADD_PARSER[mode][arg])

    parser = argparse.ArgumentParser(description='This program implement the shadowsocks protocol.',
                                     add_help='ss {local,remote} {shadowsocks,socks5_ssl}')
    sub_parsers = parser.add_subparsers(help='{local/remote} help', dest=constants.ARG_SERVER_MODE)
    for server_mode in constants.SERVER_MODES:
        server_parser = sub_parsers.add_parser(server_mode)
        for arg in constants.ARUMENTS_FOR_ADD_PARSER[server_mode].keys():
            add_argument(server_parser, server_mode, arg)

        sub_parsers_for_protocol = server_parser.add_subparsers(dest=constants.ARG_PROTOCOL_MODE)
        for protocal_mode in constants.PROTOCOL_MODES:
            protocol_parser = sub_parsers_for_protocol.add_parser(protocal_mode)
            for arg in constants.ARUMENTS_FOR_ADD_PARSER[protocal_mode].keys():
                add_argument(protocol_parser, protocal_mode, arg)

    args = parser.parse_args(args=args)
    return args
