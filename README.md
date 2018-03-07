# DESC

This project implements the [Shadowsocks](https://github.com/shadowsocks/shadowsocks) protocol using python3.5 and asyncio library
 since the original project source code is unreadble and frustrated to extend.

Shadowsocks is a proxy, 
the client is listening socks5 protocol on local forwarding encrypt socks5 data to remote proxy, 
the proxy server forwards the socket data to target host. 

Shadowsocks is mainly used for bypassing Great Firewall of China, since the data is encrypt and sent over 
normal TCP, no handshake, no fingerprint, getting away from packet inspection, it's hard to block.

# FEATURES
* shadowsocks protocol implements TCP proxy without OTA feature, no UDP  
 
# TODO

1. Filtering connections to local ip for security consideration
2. Flow control
3. Custom protocol
4. Multi threading/process for multiple user/port

# INSTALLATION
Only need to install python3.6+

## For Ubuntu 16.04
如果本地的Python3版本>3.5, 不需要再安装Python3

```
sudo apt-get install python3
sudo apt-get install python3-pip
sudo pip3 install setuptools
sudo pip3 install -U git+https://github.com/FTwOoO/pyShadowsocks.git@master#egg=pyshadowsocks
```

## For Mac OSX

```shell
pip3 install -U git+https://github.com/FTwOoO/pyShadowsocks.git@master#egg=pyshadowsocks
```

# Server side

```shell
ss shadowsocks --cipher_method aes-128-cfb --password 123456 remote --listen_port 8099 &
```

# Client side

```shell
 ss shadowsocks --cipher_method aes-128-cfb --password 123456 local --remote_host ftwo.me --remote_port 8099 --socks-port 10088
```
   
#### Mac OSX
With GoAgentX, you can use the proxy when needed(with PAC)

1. Download [GoAgentX for Mac](https://goagentx.googlecode.com/files/GoAgentX-v2.2.9.dmg).

2. Add a shell service config (to start local socks server) and then click the ON button
![GoAgentX setting for pyShadowsocks](screenshots/goagentx_shell_service_config.png)

#### iOS
[Shadowrocket](https://itunes.apple.com/cn/app/shadowrocket/id932747118?mt=8)、[Surge](https://itunes.apple.com/us/app/surge-web-developer-tool-proxy/id1040100637?mt=8) and [Potatso](https://itunes.apple.com/cn/app/tu-dou-si-potatso-qiang-da/id1070901416?l=en&mt=8)...
