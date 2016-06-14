#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 


import os.path
import ssl
import subprocess

import settings


def create_self_signed_certs():
    settings.SSL_PUBLIC_FILE = os.path.abspath(settings.SSL_PUBLIC_FILE)
    settings.SSL_RPIVATE_FILE = os.path.abspath(settings.SSL_RPIVATE_FILE)

    if not os.path.exists(settings.SSL_PUBLIC_FILE):
        os.makedirs(os.path.dirname(settings.SSL_PUBLIC_FILE), 400, exist_ok=True)
        os.makedirs(os.path.dirname(settings.SSL_RPIVATE_FILE), 400, exist_ok=True)

        try:
            subprocess.check_output('openssl req -x509 -nodes -days 3650 -newkey rsa:2048  '
                                    '-subj "/C=US/ST=Oregon/L=Portland/CN={DOMAIN_NAME}" '
                                    '-keyout {DEST_PRIVATE_PEM} '
                                    '-out {DEST_PUB_PEM}'.format(DOMAIN_NAME='example.org',
                                                                 DEST_PRIVATE_PEM=settings.SSL_RPIVATE_FILE,
                                                                 DEST_PUB_PEM=settings.SSL_PUBLIC_FILE),
                                    shell=True)

        except subprocess.CalledProcessError as ex:
            settings.CONFIG_LOG.error(ex.output)
            raise

def create_client_ssl_context():
    # The certificate is created with pymotw.com as the hostname,
    # which will not match when the example code runs
    # elsewhere, so disable hostname verification.
    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    return ssl_context


def create_server_ssl_context():
    # The certificate is created with pymotw.com as the hostname,
    # which will not match when the example code runs elsewhere,
    # so disable hostname verification.

    create_self_signed_certs()
    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
    ssl_context.check_hostname = False
    ssl_context.load_cert_chain(settings.SSL_PUBLIC_FILE, settings.SSL_RPIVATE_FILE)
    return ssl_context
