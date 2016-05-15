# -*- coding: utf-8 -*-
#

import logging
import logging.handlers
import os


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
