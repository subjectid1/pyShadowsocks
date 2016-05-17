# DESC

This project implements the [Shadowsocks](https://github.com/shadowsocks/shadowsocks) protocol using python3.5 and asyncio library
 since the original project source code is unreadble and frustrated to extend.

Shadowsocks is a proxy program, that the client is listening socks5 protocol on local(socks5 connect/UDP association), 
forward encrypt socks5 data to remote proxy, and then the proxy forward the socket data to target host. It hides the SOCKS5
 handshakes and traffic bytes from censor.

Shadowsocks is mainly used for bypassing Great Firewall of China, since the data is encrypt and sent over 
normal TCP/UDP, no handshake, no fingerprint, getting away from packet inspection, it's hard to block.

# USAGE

## INSTALLATION
### For Ubuntu 14.04

```
$ sudo apt-get install build-essential libssl-dev libffi-dev python-dev

$ pip3 install cryptography

$ sudo pip3 install -e git+https://github.com/FTwO-O/pyShadowsocks.git@master#egg=pyshadowsocks
```

### For Mac OS
Mac OS has a deprecated openssl and does not includes the header files, so you need to install openssl library manually.
See cryptography doc: [building-cryptography-on-os-x](https://cryptography.io/en/latest/installation/#building-cryptography-on-os-x)

* build openssl manually using the [script](https://github.com/FTwO-O/Build_Mac_Command_Line_Tools/blob/master/openssl.sh) 

```
$ env LDFLAGS="-L/usr/local/openssl/lib" CFLAGS="-I/usr/local/openssl/include" pip3 install cryptography

$ sudo pip3 install -e git+https://github.com/FTwO-O/pyShadowsocks.git@master#egg=pyshadowsocks
```
    
* Use brew to install openssl

```
$ brew install openssl
$ env LDFLAGS="-L$(brew --prefix openssl)/lib" CFLAGS="-I$(brew --prefix openssl)/include" pip3 install cryptography

$ sudo pip3 install -e git+https://github.com/FTwO-O/pyShadowsocks.git@master#egg=pyshadowsocks
```

### START THE SERVICE

* proxy server

```
ss remote --listen_port 8099 shadowsocks --cipher_method aes-256-cfb --password 123456 &
```
    
* local socks5 server:

```
ss local --remote_host 8.8.8.8 --remote_port 8099 shadowsocks --cipher_method aes-256-cfb --password 123456
```
   
## Mac Client
* Download [GoAgentX for Mac](https://goagentx.googlecode.com/files/GoAgentX-v2.2.9.dmg).

* Add a shell service config (to start local socks server) and then click the ON button
![GoAgentX setting for pyShadowsocks](screenshots/goagentx_shell_service_config.png)

        
# TODO

1. SOCKS5 user/password authentication
2. Filtering connections to local ip for security consideration
3. SOCKS5 over SSL
4. Custom protocol with random bytes padding, carry TCP/UPD/HTTP traffic, get away from DPI
5. Remove the cryptography library, use openssl with ctypes.