#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author: Ben Chen


class LoginType:
    auto = 'auto' # 断线重连
    request = 'request' # 二次登录
    qrcode = 'qrcode' # 扫码登录
    phone = 'phone' # 手机验证码登录
    user = 'user' # 账号密码登录

    unknow = 'unknow'
