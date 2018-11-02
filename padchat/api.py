#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author: Ben Chen
import base64
import io
from typing import Union

from tornado import gen

from .constant import LoginType
from .exceptions import UnknowLoginType, InvalidateValueError, InstanceNotInit
from .utils import send_app_msg_xml_template
from .logger import logger


class PadChatAPIMixin:
    # cmd 命令 #################################################################

    @gen.coroutine
    def init(self):
        '''
        初始化机器人
        '''
        result = yield self.send('init', self.cmd_id)
        return result

    @gen.coroutine
    def get_wx_data(self):
        '''
        获取设备实例数据
        '''
        result = yield self.send('getWxData', self.cmd_id)
        return result

    @gen.coroutine
    def login(self, type, token=None, phone=None,
              code=None, username=None, password=None):
        '''
        登录函数
        :param type: 登录类型
            Type.token: 断线重连
            Type.request: 二次登录
            Type.qrcode: 扫码登录
            Type.phone: 手机验证码登录
            Type.user: 账号密码登录
        :param token: 当type 为token 或 request时，必填项
        :param phone: 当type 为phone时，必填项。手机号
        :param code: 当type 为code时，必填项。手机验证码
        :param username: 当type 为user时，为必填项。用户名/qq号/手机号
        :param password: 为type 为user时，为必填项。登录密码
        :return: 
        
        eg. 扫码登陆
            self.login(Type.token, token='xxxxxxxx')
            
        eg. 扫码登录
            self.login(Type.qrcode)
        '''
        if not self._init:
            raise InstanceNotInit('padchat instance not init yey')
        type = getattr(LoginType, type, LoginType.unknow)
        if type == LoginType.unknow:
            raise UnknowLoginType('未知登录类型')

        data = {
            'loginType': type,
        }

        if type in (LoginType.auto, LoginType.request):
            if not token:
                raise InvalidateValueError('token must not be none')
            assert self._wx_data is not None, 'wx data must not be none'
            data.update({
                'token': token, 'wxData': self._wx_data
            })

        elif type == LoginType.phone:
            if not phone:
                raise InvalidateValueError('phone is not be none')
            data.update({
                'phone': phone, 'wxData': self._wx_data
            })

        elif type == LoginType.user:
            if not username:
                raise InvalidateValueError('username is not be none')
            if not password:
                raise InvalidateValueError('password is not be none')
            data.update({
                'username': username,
                'password': password,
                'wxData': self._wx_data
            })

        elif type == LoginType.qrcode:
            if self._wx_data:
                data.update({
                    'wxData': self._wx_data
                })

        result = yield self.send('login', cmd_id=self.cmd_id, data=data)
        return result

    @gen.coroutine
    def get_login_token(self):
        '''
        获取登录token
        :return: 
        '''
        result = yield self.send('getLoginToken', self.cmd_id)
        token = result['data'].get('token')
        self._token = token
        return result

    @gen.coroutine
    def logout(self):
        '''
        注销
        :return: 
        '''
        result = yield self.send('logout', self.cmd_id)
        logger.info('微信账号已注销退出成功')

    @gen.coroutine
    def close(self):
        '''
        关闭机器人实例（非退出微信）
        :return: 
        '''
        result = yield self.send('close', self.cmd_id)
        logger.info('退出机器人实例')

    # 用户管理 接口 #############################################################
    @gen.coroutine
    def get_contact(self, username: str):
        '''
        获取用户资料
        :param username: 对方wxid
        :return: 
        '''
        data = {
            'userId': username
        }
        result = yield self.send('getContact', self.cmd_id, data=data)
        return result

    @gen.coroutine
    def search_contact(self, username: str):
        '''
        搜索用户资料
        :param username: 对方wxid
        :return: 
        '''
        data = {
            'userId': username
        }
        result = yield self.send('searchContact', self.cmd_id, data=data)
        return result

    @gen.coroutine
    def accept_user(self, stranger: str, ticket: str):
        '''
        通过好友请求
        :param stranger: 用户stranger数据
        :param ticket: 用户ticket数据
        :return: 
        '''
        data = {
            'stranger': stranger,
            'ticket': ticket,
        }
        result = yield self.send('acceptUser', self.cmd_id, data=data)
        return result

    @gen.coroutine
    def add_contact(self, stranger: str, ticket: str, type=3, content=""):
        '''
        主动添加好友
        :param stranger: 用户stranger数据
        :param ticket: 用户ticket数据
        :param type: int 添加好友途径
        :param content: 验证信息
        :return: 
        '''
        data = {
            'stranger': stranger,
            'ticket': ticket,
            'type': type,
            'content': content,
        }
        result = yield self.send('addContact', self.cmd_id, data=data)
        return result

    @gen.coroutine
    def say_hello(self, stranger: str, ticket: str, content: str):
        '''
        打招呼
        :param stranger: 用户stranger数据
        :param ticket: 用户ticket数据
        :param content: 找招呼内容
        :return: 
        '''
        data = {
            'stranger': stranger,
            'ticket': ticket,
            'content': content,
        }
        result = yield self.send('sayHello', self.cmd_id, data=data)
        return result

    @gen.coroutine
    def delete_contact(self, username: str):
        '''
        删除好友
        :param username: 用户wxid
        :return: 
        '''
        data = {
            'userId': username
        }
        result = yield self.send('deleteContact', self.cmd_id, data=data)
        return result

    @gen.coroutine
    def set_remark(self, username: str, remark: str):
        '''
        设置好友备注
        :param username: 用户wxid
        :param remark: 备注内容
        :return: 
        '''
        data = {
            'userId': username,
            'remark': remark
        }
        result = yield self.send('setRemark', self.cmd_id, data=data)
        return result

    @gen.coroutine
    def set_head_img(self, file: Union[io.FileIO, str]):
        '''
        设置头像
        :param file: 二进制文件或base64字符串
        :param callback: 
        :return: 
        '''
        if hasattr(file, 'read'):
            file = base64.encodebytes(file.read()).decode()
        data = {
            'file': file,
        }
        result = yield self.send('setHeadImg', self.cmd_id, data=data)
        return result

    @gen.coroutine
    def sync_msg(self):
        '''
        主动同步消息
        :return: 
        '''
        result = yield self.send('syncMsg', self.cmd_id)
        return result

    @gen.coroutine
    def sync_contact(self, reset=False):
        '''
        同步通讯录
        :param reset: 若设置为true，会重置同步状态
        :return: 
        '''
        data = {
            'reset': bool(reset)
        }
        result = yield self.send('syncContact', self.cmd_id, data=data)
        return result

    @gen.coroutine
    def get_user_qrcode(self, username=None, style=0):
        '''
        获取个人二维码(仅限自己)
        :param username: 用户wxid
        :param stype: int 二维码风格0-3
        :return: 
        '''
        data = {
            'userId': username or self.user.wx_id,
            'style': style,
        }
        result = yield self.send('getUserQrcode', self.cmd_id, data=data)
        return result

    @gen.coroutine
    def get_my_info(self):
        '''
        获取个人资料
        :return: 
        '''
        result = yield self.send('getMyInfo', self.cmd_id)
        return result

    # 群管理 接口 ###############################################################
    @gen.coroutine
    def create_room(self, user_list: list):
        '''
        创建群
        备注：必须多于2个人（含2个），才会建群成功
        :param user_list: 用户wxid列表
        :return: 
        '''
        data = {
            'userList': user_list
        }
        result = yield self.send('createRoom', self.cmd_id, data=data)
        return result

    @gen.coroutine
    def get_room_members(self, group_id: str):
        '''
        获取群成员
        :param group_id: 群id
        :return: 
        '''
        data = {
            'groupId': group_id
        }
        result = yield self.send('getRoomMembers', self.cmd_id, data=data)
        return result

    @gen.coroutine
    def add_room_member(self, group_id: str, username: str):
        '''
        添加群成员
        :param group_id: 群id
        :param username: 用户wxid
        :return: 
        '''
        data = {
            'groupId': group_id,
            'userId': username,
        }
        result = yield self.send('addRoomMember', self.cmd_id, data=data)
        return result

    @gen.coroutine
    def invite_room_member(self, group_id: str, username: str):
        '''
        邀请群成员
        :param group_id: 群id
        :param username: 用户wxid
        :return: 
        '''
        data = {
            'groupId': group_id,
            'userId': username,
        }
        result = yield self.send('inviteRoomMember', self.cmd_id, data=data)
        return  result

    @gen.coroutine
    def delete_room_member(self, group_id: str, username: str):
        '''
        删除群成员
        :param group_id: 群id
        :param username: 用户wxid
        :return: 
        '''
        data = {
            'groupId': group_id,
            'userId': username,
        }
        result = yield self.send('deleteRoomMember', self.cmd_id, data=data)
        return result

    @gen.coroutine
    def quit_room(self, group_id: str):
        '''
        退群
        :param group_id: 群id
        :return: 
        '''
        data = {
            'groupId': group_id
        }
        result = yield self.send('quitRoom', self.cmd_id, data=data)
        return result

    @gen.coroutine
    def set_room_announcement(self, group_id: str, content: str):
        '''
        设置群公告
        :param group_id: 群id
        :param content: 公告内容
        :return: 
        '''
        data = {
            'groupId': group_id,
            'content': content
        }
        result = yield self.send('setRoomAnnouncement', self.cmd_id, data=data)
        return result

    @gen.coroutine
    def set_room_name(self, group_id: str, content: str):
        '''
        设置群名称
        :param groupd_id: 群id
        :param content: 群名称
        :return: 
        '''
        data = {
            'groupId': group_id,
            'content': content
        }
        result = yield self.send('setRoomName', self.cmd_id, data=data)
        return result

    @gen.coroutine
    def get_room_qrcode(self, group_id: str):
        '''
        获取群二维码
        :param group_id: 群id
        :return: 
        '''
        data = {
            'groupId': group_id
        }
        result = yield self.send('getRoomQrcode', self.cmd_id, data=data)
        return result

    # 消息 接口 #################################################################
    @gen.coroutine
    def send_msg(self, to_user_name: str, content: str, at_list: list=None):
        '''
        发送消息
        :param to_user_name: 接收者wx_id，可个人，可群组
        :param content: 发送内容
        :param at_list: 艾特wx_id列表
        :return: 
        '''
        context = {
            'toUserName': to_user_name,
            'content': content,
        }
        if at_list:
            context.update({'atList': at_list})
        result = yield self.send('sendMsg', self.cmd_id, data=context)
        return result

    @gen.coroutine
    def send_app_msg(self, username: str, title: str, des: str, url: str,
                   thumburl: str, appid=None, sdkver=None):
        '''
        发送App消息
        :param username: 接收者wxid
        :param title: 标题
        :param des: 描述
        :param url: 链接url
        :param thumburl: 缩略图url
        :param appid: appid，可忽略
        :param sdkver: sdk版本，可忽略
        :return: 
        '''
        context = {
            'title': title,
            'des': des,
            'url': url,
            'thumburl': thumburl,
            'appid': appid or '',
            'sdkver': sdkver or '',
        }
        data = {
            'toUserName': username,
            'content': send_app_msg_xml_template(context),
        }
        result = yield self.send('sendAppMsg', self.cmd_id, data=data)
        return result

    @gen.coroutine
    def send_image(self, username: str, file: Union[io.FileIO, str]):
        '''
        发送图片
        :param username: 接收者wxid
        :param file: 二进制文件或base64字符串
        :return: 
        '''
        if hasattr(file, 'read'):
            file = base64.encodebytes(file.read()).decode()
        data = {
            'toUserName': username,
            'file': file
        }
        result = yield self.send('sendImage', self.cmd_id, data=data)
        return result

    @gen.coroutine
    def send_voice(self, username: str, file: Union[io.FileIO, str], time: int):
        '''
        发送语音
        :param username: 接收者id
        :param file: 二进制文件或base64字符串，silk格式的语音文件
        :param time: 语音时长，毫秒单位
        :param callback: 
        :return: 
        '''
        if hasattr(file, 'read'):
            file = base64.encodebytes(file.read()).decode()
        data = {
            'toUserName': username,
            'file': file,
            'time': time,
        }
        result = yield self.send('sendVoice', self.cmd_id, data=data)
        return result

    @gen.coroutine
    def share_card(self, username: str, content: str, user_id: str):
        '''
        分享名片
        :param username: 接收者id
        :param content: 分享内容
        :param user_id: 被分享者id
        :return: 
        '''
        data = {
            'toUserName': username,
            'content': content,
            'userId': user_id
        }
        result = yield self.send('shareCard', self.cmd_id, data=data)
        return result

    # 获取图片、文件接口 #########################################################
    @gen.coroutine
    def get_msg_image(self, raw_data):
        '''
        获取图片
        :param raw_data: 拿到的push数据，就是raw_data，不用做任何处理
        :return: 
        '''
        if 'rawMsgData' not in raw_data:
            raw_data = {'rawMsgData': raw_data}
        result = yield self.send('getMsgImage', self.cmd_id, data=raw_data)
        return result

    @gen.coroutine
    def get_msg_video(self, raw_data):
        '''
        获取视频
        :param raw_data: 拿到的push数据，就是raw_data，不用做任何处理
        :return: 
        '''
        if 'rawMsgData' not in raw_data:
            raw_data = {'rawMsgData': raw_data}
        result = yield self.send('getMsgVideo', self.cmd_id, data=raw_data)
        return result

    @gen.coroutine
    def get_msg_voice(self, raw_data):
        '''
        获取音频
        :param raw_data: 拿到的push数据，就是raw_data，不用做任何处理
        :return: 
        '''
        if 'rawMsgData' not in raw_data:
            raw_data = {'rawMsgData': raw_data}
        result = yield self.send('getMsgVoice', self.cmd_id, data=raw_data)
        return result

    # 转账 接口 #################################################################
    @gen.coroutine
    def query_transfer(self, raw_data):
        '''
        查看转账消息
        :param raw_data: 拿到的push数据，就是raw_data，不用做任何处理
        :return: 
        '''
        raise DeprecationWarning('this method has deprecation')
        if 'rawMsgData' not in raw_data:
            raw_data = {'rawMsgData': raw_data}
        result = yield self.send('queryTransfer', self.cmd_id, data=raw_data)
        return result

    @gen.coroutine
    def accept_transfer(self, raw_data):
        '''
        接受转账
        :param raw_data: 拿到的push msg消息，就是raw_data，不用做任何处理
        :return: 
        '''
        raise DeprecationWarning('this method has deprecation')
        if 'rawMsgData' not in raw_data:
            raw_data = {'rawMsgData': raw_data}
        result = yield self.send('acceptTransfer', self.cmd_id, data=raw_data)
        return result

    # 红包 接口 #################################################################
    @gen.coroutine
    def receive_red_packet(self, raw_data):
        '''
        接收红包
        该接口并未正式领取红包，但领取红包前必须调用该函数，然后在该指令的回调函数中，或稍后
        再发送领取红包指令。
        领取红包以及查看红包信息，都必须先调用该函数，否则会执行失败
        :param raw_data: 拿到的push数据，就是raw_data，不用做任何处理
        :return: 
        '''
        if 'rawMsgData' not in raw_data:
            raw_data = {'rawMsgData': raw_data}
        result = yield self.send('receiveRedPacket', self.cmd_id, data=raw_data)
        return result

    @gen.coroutine
    def open_red_packet(self, raw_data, key):
        '''
        领取红包
        :param raw_data: 拿到的push数据，就是raw_data，不用做任何处理
        :param key: 从接收红包接口中获取
        :return: 
        '''
        if 'rawMsgData' not in raw_data:
            raw_data = {
                'rawMsgData': raw_data,
            }
        raw_data.update({'key': key})
        result = yield self.send('openRedPacket', self.cmd_id, data=raw_data)
        return result

    @gen.coroutine
    def query_red_packet(self, raw_data, key):
        '''
        查看红包信息
        :param raw_data: 拿到的push数据，就是raw_data，不用做任何处理
        :param key: 从接收红包接口中获取
        :return: 
        '''
        if 'rawMsgData' not in raw_data:
            raw_data = {'rawMsgData': raw_data}
        result = yield self.send('queryRedPacket', self.cmd_id, data=raw_data)
        return result

