# The MIT License (MIT)
#
# Copyright (c) 2014 Richard Moore
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import sys

sys.path.append('../pyaes')

from pyaes import *
from pyaes.aes import Decrypter, Encrypter, PADDING_NONE, encrypt_stream, decrypt_stream
import pyaes
from Crypto.Cipher import AES as KAES
from Crypto.Util import Counter as KCounter
import time
import os
import random
import io
import unittest


class ConfigTest(unittest.TestCase):
    def test_all_aes(self):
        key = os.urandom(32)
        plaintext = os.urandom(1000)

        for mode_name in pyaes.AESModesOfOperation:
            mode = pyaes.AESModesOfOperation[mode_name]
            print(mode.name)

            kw = dict(key=key)
            if mode_name in ('cbc', 'cfb', 'ofb'):
                kw['iv'] = os.urandom(16)

            encrypter = Encrypter(mode(**kw))
            ciphertext = b''

            # Feed the encrypter random number of bytes at a time
            index = 0
            while index < len(plaintext):
                length = random.randint(1, 128)
                if index + length > len(plaintext): length = len(plaintext) - index
                ciphertext += encrypter.feed(plaintext[index: index + length])
                index += length
            ciphertext += encrypter.feed(None)

            decrypter = Decrypter(mode(**kw))
            decrypted = b''

            # Feed the decrypter random number of bytes at a time
            index = 0
            while index < len(ciphertext):
                length = random.randint(1, 128)
                if index + length > len(ciphertext): length = len(ciphertext) - index
                decrypted += decrypter.feed(ciphertext[index: index + length])
                index += length
            decrypted += decrypter.feed(None)

            passed = decrypted == plaintext
            cipher_length = len(ciphertext)
            print("  cipher-length=%(cipher_length)s passed=%(passed)s" % locals())

        # Test block modes of operation with no padding
        plaintext = os.urandom(1024)

        for mode_name in ['ecb', 'cbc']:
            mode = pyaes.AESModesOfOperation[mode_name]
            print(mode.name + ' (no padding)')

            kw = dict(key=key)
            if mode_name == 'cbc':
                kw['iv'] = os.urandom(16)

            encrypter = Encrypter(mode(**kw), padding=PADDING_NONE)
            ciphertext = b''

            # Feed the encrypter random number of bytes at a time
            index = 0
            while index < len(plaintext):
                length = random.randint(1, 128)
                if index + length > len(plaintext): length = len(plaintext) - index
                ciphertext += encrypter.feed(plaintext[index: index + length])
                index += length
            ciphertext += encrypter.feed(None)

            if len(ciphertext) != len(plaintext):
                print('  failed to encrypt with correct padding')

            decrypter = Decrypter(mode(**kw), padding=PADDING_NONE)
            decrypted = b''

            # Feed the decrypter random number of bytes at a time
            index = 0
            while index < len(ciphertext):
                length = random.randint(1, 128)
                if index + length > len(ciphertext): length = len(ciphertext) - index
                decrypted += decrypter.feed(ciphertext[index: index + length])
                index += length
            decrypted += decrypter.feed(None)

            passed = decrypted == plaintext
            cipher_length = len(ciphertext)
            print("  cipher-length=%(cipher_length)s passed=%(passed)s" % locals())

        plaintext = os.urandom(1000)

        for mode_name in pyaes.AESModesOfOperation:
            mode = pyaes.AESModesOfOperation[mode_name]
            print(mode.name + ' (stream operations)')

            kw = dict(key=key)
            if mode_name in ('cbc', 'cfb', 'ofb'):
                kw['iv'] = os.urandom(16)

            moo = mode(**kw)
            output = io.BytesIO()
            encrypt_stream(moo, io.BytesIO(plaintext), output)
            output.seek(0)
            ciphertext = output.read()

            moo = mode(**kw)
            output = io.BytesIO()
            decrypt_stream(moo, io.BytesIO(ciphertext), output)
            output.seek(0)
            decrypted = output.read()

            passed = decrypted == plaintext
            cipher_length = len(ciphertext)

            self.assertEqual(decrypted, plaintext)

    def test_bench_with_Crypto(self):

        for mode in ['CBC', 'CTR', 'CFB', 'ECB', 'OFB']:

            (tt_ksetup, tt_kencrypt, tt_kdecrypt) = (0.0, 0.0, 0.0)
            (tt_setup, tt_encrypt, tt_decrypt) = (0.0, 0.0, 0.0)
            count = 0

            for key_size in (128, 192, 256):

                for test in range(1, 8):
                    key = os.urandom(key_size // 8)

                    if mode == 'CBC':
                        iv = os.urandom(16)
                        plaintext = [os.urandom(16) for x in range(0, test)]

                        t0 = time.time()
                        kaes = KAES.new(key, KAES.MODE_CBC, IV=iv)
                        kaes2 = KAES.new(key, KAES.MODE_CBC, IV=iv)
                        tt_ksetup += time.time() - t0

                        t0 = time.time()
                        aes = AESModeOfOperationCBC(key, iv=iv)
                        aes2 = AESModeOfOperationCBC(key, iv=iv)
                        tt_setup += time.time() - t0

                    elif mode == 'CFB':
                        iv = os.urandom(16)
                        plaintext = [os.urandom(test * 5) for x in range(0, test)]

                        t0 = time.time()
                        kaes = KAES.new(key, KAES.MODE_CFB, IV=iv, segment_size=test * 8)
                        kaes2 = KAES.new(key, KAES.MODE_CFB, IV=iv, segment_size=test * 8)
                        tt_ksetup += time.time() - t0

                        t0 = time.time()
                        aes = AESModeOfOperationCFB(key, iv=iv, segment_size=test)
                        aes2 = AESModeOfOperationCFB(key, iv=iv, segment_size=test)
                        tt_setup += time.time() - t0

                    elif mode == 'ECB':
                        plaintext = [os.urandom(16) for x in range(0, test)]

                        t0 = time.time()
                        kaes = KAES.new(key, KAES.MODE_ECB)
                        kaes2 = KAES.new(key, KAES.MODE_ECB)
                        tt_ksetup += time.time() - t0

                        t0 = time.time()
                        aes = AESModeOfOperationECB(key)
                        aes2 = AESModeOfOperationECB(key)
                        tt_setup += time.time() - t0

                    elif mode == 'OFB':
                        iv = os.urandom(16)
                        plaintext = [os.urandom(16) for x in range(0, test)]

                        t0 = time.time()
                        kaes = KAES.new(key, KAES.MODE_OFB, IV=iv)
                        kaes2 = KAES.new(key, KAES.MODE_OFB, IV=iv)
                        tt_ksetup += time.time() - t0

                        t0 = time.time()
                        aes = AESModeOfOperationOFB(key, iv=iv)
                        aes2 = AESModeOfOperationOFB(key, iv=iv)
                        tt_setup += time.time() - t0

                    elif mode == 'CTR':
                        text_length = \
                            [None, 3, 16, 127, 128, 129, 1500, 10000, 100000, 10001, 10002, 10003, 10004, 10005, 10006,
                             10007,
                             10008][test]
                        if test < 6:
                            plaintext = [os.urandom(text_length)]
                        else:
                            plaintext = [os.urandom(text_length) for x in range(0, test)]

                        t0 = time.time()
                        kaes = KAES.new(key, KAES.MODE_CTR, counter=KCounter.new(128, initial_value=0))
                        kaes2 = KAES.new(key, KAES.MODE_CTR, counter=KCounter.new(128, initial_value=0))
                        tt_ksetup += time.time() - t0

                        t0 = time.time()
                        aes = AESModeOfOperationCTR(key, counter=Counter(initial_value=0))
                        aes2 = AESModeOfOperationCTR(key, counter=Counter(initial_value=0))
                        tt_setup += time.time() - t0

                    count += 1

                    t0 = time.time()
                    kenc = [kaes.encrypt(p) for p in plaintext]
                    tt_kencrypt += time.time() - t0

                    t0 = time.time()
                    enc = [aes.encrypt(p) for p in plaintext]
                    tt_encrypt += time.time() - t0

                    if kenc != enc:
                        print("Test: mode=%s operation=encrypt key_size=%d text_length=%d trial=%d" % (
                            mode, key_size, len(plaintext), test))
                        raise Exception('Failed encypt test case (%s)' % mode)

                    t0 = time.time()
                    dt1 = [kaes2.decrypt(k) for k in kenc]
                    tt_kdecrypt += time.time() - t0

                    t0 = time.time()
                    dt2 = [aes2.decrypt(k) for k in kenc]
                    tt_decrypt += time.time() - t0

                    if plaintext != dt2:
                        print("Test: mode=%s operation=decrypt key_size=%d text_length=%d trial=%d" % (
                            mode, key_size, len(plaintext), test))
                        raise Exception('Failed decypt test case (%s)' % mode)

            better = (tt_setup + tt_encrypt + tt_decrypt) / (tt_ksetup + tt_kencrypt + tt_kdecrypt)
            print("Mode: %s" % mode)
            print("  Average time: PyCrypto: encrypt=%fs decrypt=%fs setup=%f" % (
                tt_kencrypt / count, tt_kdecrypt / count, tt_ksetup / count))
            print("  Average time: pyaes:    encrypt=%fs decrypt=%fs setup=%f" % (
                tt_encrypt / count, tt_decrypt / count, tt_setup / count))
            print("  Native better by: %dx" % better)

    def test_PKCS7(self):
        from pyaes.aes import append_PKCS7_padding, strip_PKCS7_padding

        byte = 'A'

        # Python 3 compatibility
        # convert sample byte to bytes type, so that data = byte * i yields bytes, not str
        byte = bytes(byte, 'utf-8')

        for i in range(0, 17):
            data = byte * i
            padded = append_PKCS7_padding(data)
            self.assertEqual(strip_PKCS7_padding(padded), data)
