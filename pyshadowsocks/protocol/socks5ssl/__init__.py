#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 


import ssl

import settings


def create_certs():
    import subprocess
    subprocess.check_output('openssl req -x509 -nodes -days 3650 -newkey rsa:2048  '
                            '-subj "/C=US/ST=Oregon/L=Portland/CN={DOMAIN_NAME}" '
                            '-keyout {DEST_PRIVATE_PEM} '
                            '-out {DEST_PUB_PEM}'.format(DOMAIN_NAME='example.org',
                                                         DEST_PRIVATE_PEM=settings.SSL_RPIVATE_FILE,
                                                         DEST_PUB_PEM=settings.SSL_PUBLIC_FILE),
                            shell=True)


def create_client_ssl_context():
    # The certificate is created with pymotw.com as the hostname,
    # which will not match when the example code runs
    # elsewhere, so disable hostname verification.
    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    ssl_context.check_hostname = False
    ssl_context.load_verify_locations(settings.SSL_PUBLIC_FILE)


def create_server_ssl_context():
    # The certificate is created with pymotw.com as the hostname,
    # which will not match when the example code runs elsewhere,
    # so disable hostname verification.
    ssl_context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
    ssl_context.check_hostname = False
    ssl_context.load_cert_chain(settings.SSL_PUBLIC_FILE, settings.SSL_RPIVATE_FILE)
