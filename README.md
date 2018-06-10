
项目重新实现了 [Shadowsocks](https://github.com/shadowsocks/shadowsocks)协议（但不完全实现所有特性），主要是因为原来的Python版本过于繁杂难以修改，且用了很多类C的API，并不Pythonic。

为了实现长久的可用性（Python版本和第三方库升级都不会影响）和一条命令即可安装（即便是运维友好的Golang实现的程序，也不能那么简洁的达到这个目标），只使用Python3的标准库，除了加密这标准库没有就拿了openssl自己编译成动态库打包进程序，有点恶心，但也算实现了不那么长久的可用性（如果openssl只使用了标准C的话，那可用性还是不错的），最好是能找一个一个运算量比较低的高强度加密算法及其纯Python实现。

Shadowsocks算是SOCKS5协议的简化+加密，足够简单可用(如果要在效率上改进，只能从TCP下手了)


# FEATURES
* 只实现了TCP代理，UDP未实现，OTA特性未实现
* 加密方法只有AES-128/256.

# Server side
如果本地的Python3版本>3.6, 不需要再安装Python3, Ubuntu 16.04用如下命令安装和启动

```shell
sudo apt-get install python3
sudo apt-get install python3-pip

sudo pip3 install setuptools
sudo pip3 install -U git+https://github.com/FTwOoO/pyShadowsocks.git@master#egg=pyshadowsocks

ss shadowsocks --cipher_method aes-128-cfb --password 123456 remote --listen_port 8099 &
```

或者使用Docker镜像安装:

```
docker run -d -p 9067:9067 fooltwo/pyshadowsocks python ss.py  shadowsocks  --cipher_method aes-128-cfb --password 123456 remote --listen_port 8099
```


# Client side

1. 使用GoAgentX添加一个shell service(GoAgentX内置了PAC的设置和修改系统代理的功能）:
```shell
pip3 install -U git+https://github.com/FTwOoO/pyShadowsocks.git@master#egg=pyshadowsocks
 ss shadowsocks --cipher_method aes-128-cfb --password 123456 local --remote_host ftwo.me --remote_port 8099 --socks-port 10088
```

2. 或者使用[gsc](https://github.com/FTwOoO/go-shadowsocks-client)，自动设置系统代理，自动判断是否需要走代理，无需额外的配置:
```
gsc --cipher AES-128-CFB --password 123456 --c "ftwo.me:8099"
```

 
# TODO
1. Filtering connections to local ip for security consideration
2. add AHEAD encryption method

