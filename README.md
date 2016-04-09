USAGE
======

proxy server:

    python ss.py remote --listen_port 8033 shadowsocks --cipher_method aes-256-cfb --password Xbd8.#xx
    
local:

    python ss.py local --listen_port 1080 --remote_host ec2-52-79-80-31.ap-northeast-2.compute.amazonaws.com --remote_port 8033 
    shadowsocks --cipher_method aes-256-cfb --password Xbd8.#xx