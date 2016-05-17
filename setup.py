#!/usr/bin/env python3

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md'), encoding='utf-8').read()

setup(
    name='pyshadowsocks',
    version='0.2',

    author='booopooob@gmail.com',
    author_email='booopooob@gmail.com',
    url='https://github.com/FTwO-O/pyShadowsocks',
    license='MIT',

    description="forward the encrpted socks5 data to bypass firewall",
    keywords="GFW shadowsocks",

    long_description=README,

    packages=find_packages(),

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.md'],
        # And include any *.msg files found in the 'hello' package, too:
        'pac': ['*.pac'],
    },

    install_requires=['cryptography>=1.2.3'],

    platforms='any',
    include_package_data = True,

    zip_safe=False,

    classifiers=[
        "Development Status :: beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Topic :: Internet",
        "Topic :: Utilities"
    ],

     entry_points="""
    [console_scripts]
    ss = pyshadowsocks.ss:main
    """,

)
