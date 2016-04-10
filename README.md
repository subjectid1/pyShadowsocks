# DESC
This project implements the [Shadowsocks](https://github.com/shadowsocks/shadowsocks) protocol using python3 and asyncio std library
 since the original project source code is frustrated to extend.

Shadowsocks is a proxy program that listening socks5 protocol on local(socks5 connect/UDP association), 
forward socks5 data to remote, and then forward the socket to target host. Actually 'socks5 forwarder' is more appropriate
 then the named 'shadowsocks'.

Shadowsocks is mainly used for bypassing GFW(Great Firewall of China), since the data is encrypt and sent over 
normal TCP/UDP, no session, no handshake, no protocol mark, getting away from packet inspection, it's hard to block
 by firewall.



# USAGE

* proxy server

        python ss.py remote --listen_port 8033 shadowsocks --cipher_method aes-256-cfb --password 123456
    
* local socks5:

        
        python ss.py local --listen_port 1080 --remote_host ec2-52-79-80-31.ap-northeast-2.compute.amazonaws.com --remote_port 8033 
        shadowsocks --cipher_method aes-256-cfb --password 123456
        
