# DESC

This project implements the [Shadowsocks](https://github.com/shadowsocks/shadowsocks) protocol using python3.5 and asyncio library
 since the original project source code is unreadble and frustrated to extend.

Shadowsocks is a proxy program, that the client is listening socks5 protocol on local(socks5 connect/UDP association), 
forward encrypt socks5 data to remote proxy, and then the proxy forward the socket data to target host. It hides the SOCKS5
 handshakes and traffic bytes from censor.

Shadowsocks is mainly used for bypassing Great Firewall of China, since the data is encrypt and sent over 
normal TCP/UDP, no handshake, no fingerprint, getting away from packet inspection, it's hard to block.



# USAGE

## DEPENDENCIES
### For Ubuntu 14.04

```
$ sudo apt-get install build-essential libssl-dev libffi-dev python-dev
$ pip3 install cryptography
```
### For Mac OS
Mac OS has a deprecated openssl and does not includes the header files, so you need to install it.
[See cryptography doc: building-cryptography-on-os-x](https://cryptography.io/en/latest/installation/#building-cryptography-on-os-x)

* [build openssl dylib to /usr/local/ manully](https://github.com/FTwO-O/Build_Mac_Command_Line_Tools/blob/master/openssl.sh) and use it

```
env LDFLAGS="-L/usr/local/openssl/lib" CFLAGS="-I/usr/local/openssl/include" pip3 install cryptography
```
    
* Use brew to install openssl
```
$ brew install openssl
$ env LDFLAGS="-L$(brew --prefix openssl)/lib" CFLAGS="-I$(brew --prefix openssl)/include" pip3 install cryptography
```

### START

* proxy server

```
ss remote --listen_port 9999 shadowsocks --cipher_method aes-256-cfb --password 123456
```
    
* local socks5:

```
ss local --listen_port 1080 --remote_host vps_host.com --remote_port 9999
shadowsocks --cipher_method aes-256-cfb --password 123456
```
        
# TODO

1. SOCKS5 user/password authentication
2. filtering connections to local ip for security consideration
3. SOCKS5 over SSL
4. Custom protocol with random bytes padding, carry TCP/UPD/HTTP traffic, get away from DPI