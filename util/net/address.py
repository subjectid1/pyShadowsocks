#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: booopooob@gmail.com
# 
# Info:
#
#
import socket
import constants


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
