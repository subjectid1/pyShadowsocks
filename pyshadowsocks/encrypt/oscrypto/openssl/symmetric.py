# coding: utf-8
from __future__ import unicode_literals, division, absolute_import, print_function

import math
from ctypes import create_string_buffer

from ._errors import pretty_message
from ._ffi import new, null, is_null, buffer_from_bytes, bytes_from_buffer, deref
from ._libcrypto import libcrypto, handle_openssl_error
from ._types import type_name, byte_cls


def create_context(cipher, key, iv, padding=True, encrypt=True):
    """
    Encrypts plaintext

    :param cipher:
        A unicode string of "aes128", "aes192", "aes256", "des",
        "tripledes_2key", "tripledes_3key", "rc2", "rc4"

    :param key:
        The encryption key - a byte string 5-32 bytes long

    :param data:
        The plaintext - a byte string

    :param iv:
        The initialization vector - a byte string - unused for RC4

    :param padding:
        Boolean, if padding should be used - unused for RC4

    :raises:
        ValueError - when any of the parameters contain an invalid value
        TypeError - when any of the parameters are of the wrong type
        OSError - when an error is returned by OpenSSL

    :return:
        A byte string of the ciphertext
    """

    if not isinstance(key, byte_cls):
        raise TypeError(pretty_message(
            '''
            key must be a byte string, not %s
            ''',
            type_name(key)
        ))

    if cipher != 'rc4' and not isinstance(iv, byte_cls):
        raise TypeError(pretty_message(
            '''
            iv must be a byte string, not %s
            ''',
            type_name(iv)
        ))

    if cipher != 'rc4' and padding is None:
        raise ValueError('padding must be specified')

    evp_cipher_ctx = None

    try:

        evp_cipher = _get_evp_cipher(cipher)
        key_size = libcrypto.EVP_CIPHER_key_length(evp_cipher)
        iv_size = libcrypto.EVP_CIPHER_iv_length(evp_cipher)

        if key_size > 0 and len(key) != key_size:
            raise ValueError('key size does not match, need %d bytes' % key_size)
        elif iv_size > 0 and len(iv) != iv_size:
            raise ValueError('iv size does not match, need %d bytes' % iv_size)

        evp_cipher_ctx = libcrypto.EVP_CIPHER_CTX_new()
        if is_null(evp_cipher_ctx):
            handle_openssl_error(0)

        if iv is None:
            iv = null()

        res = libcrypto.EVP_CipherInit_ex(evp_cipher_ctx, evp_cipher, null(), key, iv, int(encrypt))
        handle_openssl_error(res)

        if padding is not None:
            res = libcrypto.EVP_CIPHER_CTX_set_padding(evp_cipher_ctx, int(padding))
            handle_openssl_error(res)

        return evp_cipher_ctx
    except OSError:
        libcrypto.EVP_CIPHER_CTX_free(evp_cipher_ctx)
        raise


def update(evp_cipher_ctx, data):
    if not isinstance(data, byte_cls):
        raise TypeError(pretty_message(
            '''
            data must be a byte string, not %s
            ''',
            type_name(data)
        ))

    try:
        buffer_size = _get_buffer_size(evp_cipher_ctx, data)

        buffer = buffer_from_bytes(buffer_size)
        output_length = new(libcrypto, 'int *')

        res = libcrypto.EVP_CipherUpdate(evp_cipher_ctx, buffer, output_length, data, len(data))
        handle_openssl_error(res)

        output = bytes_from_buffer(buffer, deref(output_length))

        return output

    except OSError:
        if evp_cipher_ctx:
            libcrypto.EVP_CIPHER_CTX_free(evp_cipher_ctx)
        raise


def final(evp_cipher_ctx):
    try:

        buffer = buffer_from_bytes(128)
        output_length = new(libcrypto, 'int *')

        res = libcrypto.EVP_CipherFinal_ex(evp_cipher_ctx, buffer, output_length)
        handle_openssl_error(res)

        output = bytes_from_buffer(buffer, deref(output_length))

        return output

    except OSError:
        if evp_cipher_ctx:
            libcrypto.EVP_CIPHER_CTX_free(evp_cipher_ctx)
        raise


def destrop_context(evp_cipher_ctx):
    if evp_cipher_ctx:
        libcrypto.EVP_CIPHER_CTX_free(evp_cipher_ctx)


def get_key_and_iv_length(cipher):
    evp_cipher = _get_evp_cipher(cipher)
    key_size = libcrypto.EVP_CIPHER_key_length(evp_cipher)
    iv_size = libcrypto.EVP_CIPHER_iv_length(evp_cipher)
    return key_size, iv_size


def _get_evp_cipher(cipher):
    c_cipher_name = create_string_buffer(cipher.encode('utf-8'))
    evp_cipher = libcrypto.EVP_get_cipherbyname(c_cipher_name)
    assert (evp_cipher is not None and evp_cipher != 0)
    return evp_cipher


def _get_buffer_size(evp_cipher_ctx, data):
    block_size = libcrypto.EVP_CIPHER_CTX_block_size(evp_cipher_ctx)
    return block_size * int(math.ceil(len(data) / block_size))
