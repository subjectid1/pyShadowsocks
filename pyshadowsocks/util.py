import argparse
import logging
import logging.handlers
import os
import resource
import socket
from typing import Dict

import constants


def parse_args_new(args=None):
    def add_argument(parser, mode, arg):
        parser.add_argument('--' + arg, dest=arg, **constants.ARUMENTS_FOR_ADD_PARSER[mode][arg])

    parser = argparse.ArgumentParser(description='This program implement the shadowsocks protocol.',
                                     add_help='ss {local,remote} {shadowsocks,socks5_ssl}')

    sub_parsers_for_protocol = parser.add_subparsers(dest=constants.ARG_PROTOCOL_MODE)
    for protocal_mode in constants.PROTOCOL_MODES:
        protocol_parser = sub_parsers_for_protocol.add_parser(protocal_mode)
        for arg in constants.ARUMENTS_FOR_ADD_PARSER[protocal_mode].keys():
            add_argument(protocol_parser, protocal_mode, arg)

        sub_parsers = protocol_parser.add_subparsers(dest=constants.ARG_SERVER_MODE)
        for server_mode in constants.SERVER_MODES:
            server_parser = sub_parsers.add_parser(server_mode)
            for arg in constants.ARUMENTS_FOR_ADD_PARSER[server_mode].keys():
                add_argument(server_parser, server_mode, arg)

    args = parser.parse_args(args=args)
    return args


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


def what_type_of_the_address(address):
    assert (isinstance(address, str))

    for family in (socket.AF_INET, socket.AF_INET6):
        try:
            r = socket.inet_pton(family, address)
            return {socket.AF_INET: constants.SOCKS5_ADDRTYPE_IPV4,
                    socket.AF_INET6: constants.SOCKS5_ADDRTYPE_IPV6}[family]

        except (TypeError, ValueError, OSError, IOError):
            pass
    return constants.SOCKS5_ADDRTYPE_HOST


def get_logger(name: str, level) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level=level)

    log_files = [
        '/var/logs/pyShadowsocks/{}.log'.format(name),
        '~/.pyShadowsocks/{}.log'.format(name)
    ]

    log_file = None
    for test_file in log_files:
        try:
            test_file = os.path.expanduser(test_file)
            os.makedirs(os.path.dirname(test_file), exist_ok=True)
            open(test_file, 'ab').write(b'xxxxx')
        except PermissionError:
            continue
        else:
            log_file = test_file
            break

    assert (log_file is not None)
    handler = logging.handlers.TimedRotatingFileHandler(log_file, encoding='utf8', when='D')
    formatter = logging.Formatter('[%(asctime)s-%(levelname)s]:%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def get_resource_usage_report():
    r = resource.getrusage(0)

    key_to_description = {
        "ru_utime": "time in user mode (float)",
        "ru_stime": "time in system mode (float)",
        "ru_maxrss": "maximum resident set size",
        "ru_ixrss": "shared memory size",
        "ru_idrss": "unshared memory size",
        "ru_isrss": "unshared stack size",
        "ru_minflt": "page faults not requiring I/O",
        "ru_majflt": "page faults requiring I/O",
        "ru_nswap": "number of swap outs",
        "ru_inblock": "block input operations",
        "ru_oublock": "block output operations",
        "ru_msgsnd": "messages sent",
        "ru_msgrcv": "messages received",
        "ru_nsignals": "signals received",
        "ru_nvcsw": "voluntary context switches",
        "ru_nivcsw": "involuntary context switches",
    }

    return dict([(v, getattr(r, k)) for k, v in key_to_description.items()])


def set_open_file_limit_up_to(limit=65536):
    import settings

    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    limit = max(soft, limit)
    limit = min(limit, hard)

    while limit > soft:
        try:
            resource.setrlimit(resource.RLIMIT_NOFILE, (limit, hard))
            break
        except ValueError:
            limit -= 256
        except:
            settings.CONFIG_LOG.exception('unexpected exception')

    soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
    settings.CONFIG_LOG.info('open file limit set to %d:%d', soft, hard)
    return (soft, hard)


if __name__ == '__main__':
    print(set_open_file_limit_up_to())
