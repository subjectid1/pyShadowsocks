# -*- coding: utf-8 -*-
#

import logging
import os


def get_logger(name:str, level)-> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    utils_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(utils_dir)
    log_file = os.path.join(project_dir, 'logs/{}.log'.format(name))
    if not os.path.exists(log_file):
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        open(log_file, 'ab').close()
    # TODO: change to use rotatingFileLogger
    ch = logging.FileHandler(log_file, encoding='utf8')
    # ch.setLevel(level)
    formatter = logging.Formatter('[%(asctime)s-%(levelname)s]:%(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
