# DESC

This project implements the [Shadowsocks](https://github.com/shadowsocks/shadowsocks) protocol using python3.5 and asyncio library
 since the original project source code is unreadble and frustrated to extend.

Shadowsocks is a proxy, 
the client is listening socks5 protocol on local forwarding encrypt socks5 data to remote proxy, 
the proxy server forwards the socket data to target host. 

Shadowsocks is mainly used for bypassing Great Firewall of China, since the data is encrypt and sent over 
normal TCP, no handshake, no fingerprint, getting away from packet inspection, it's hard to block.

# FEATURES
* implements TCP proxy without OTA feature, no UDP
* only AES-128/256 encryption supported now.

# Server side
system:Ubuntu 16.04, 如果本地的Python3版本>3.6, 不需要再安装Python3

```shell
sudo apt-get install python3
sudo apt-get install python3-pip
sudo pip3 install setuptools
sudo pip3 install -U git+https://github.com/FTwOoO/pyShadowsocks.git@master#egg=pyshadowsocks
ss shadowsocks --cipher_method aes-128-cfb --password 123456 remote --listen_port 8099 &
```

# Client side

1. Within GoAgentX, Add a shell service config with the script:
```shell
pip3 install -U git+https://github.com/FTwOoO/pyShadowsocks.git@master#egg=pyshadowsocks
 ss shadowsocks --cipher_method aes-128-cfb --password 123456 local --remote_host ftwo.me --remote_port 8099 --socks-port 10088
```

2. Use another shadowsocks client [gsc](https://github.com/FTwOoO/go-shadowsocks-client) which will auto set the system proxy setting:
```
gsc --cipher AES-128-CFB --password 123456 --c "ftwo.me:8099"
```

 
# TODO
1. Filtering connections to local ip for security consideration
2. add AHEAD encryption method

