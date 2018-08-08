#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author: Ben Chen
import base64
import io
from typing import Union

from .constant import LoginType
from .exceptions import UnknowLoginType, InvalidateValueError, InstanceNotInit
from .utils import send_app_msg_xml_template


class PadChatAPIMixin:
    # cmd 命令 #################################################################

    def init(self, callback='init_callback'):
        '''
        初始化机器人
        '''
        self.send('init', self.cmd_id, callback=callback)

    def get_wx_data(self, callback='get_wx_data_callback'):
        '''
        获取设备实例数据
        '''
        self.send('getWxData', self.cmd_id, callback=callback)

    def login(self, type, token=None, phone=None,
              code=None, username=None, password=None,
              callback='login_callback'):
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
        :param callback: 回调函数，尽量不修改
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
        if type in (LoginType.token, LoginType.request):
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
        self.send('login', cmd_id=self.cmd_id, callback=callback, data=data)

    def get_login_token(self, callback='get_login_token_callback'):
        '''
        获取登录token
        :param callback: 
        :return: 
        '''
        self.send('getLoginToken', self.cmd_id, callback=callback)

    def logout(self, callback='logout_callback'):
        '''
        注销
        :param callback: 
        :return: 
        '''
        self.send('logout', self.cmd_id, callback=callback)

    def close(self, callback='close_callback'):
        '''
        关闭机器人实例（非退出微信）
        :param callback: 
        :return: 
        '''
        self.send('close', self.cmd_id, callback=callback)

    # 用户管理 接口 #############################################################
    def get_contact(self, username: str, callback='get_contact_callback'):
        '''
        获取用户资料
        :param username: 对方wxid
        :param callback: 
        :return: 
        '''
        data = {
            'userId': username
        }
        self.send('getContact', self.cmd_id, callback=callback, data=data)

    def search_contact(self, username: str, callback='search_contact_callback'):
        '''
        搜索用户资料
        :param username: 对方wxid
        :param callback: 
        :return: 
        '''
        data = {
            'userId': username
        }
        self.send('searchContact', self.cmd_id, callback=callback, data=data)

    def accept_user(self, stranger: str, ticket: str, callback='accept_user_callback'):
        '''
        通过好友请求
        :param stranger: 用户stranger数据
        :param ticket: 用户ticket数据
        :param callback: 
        :return: 
        '''
        data = {
            'stranger': stranger,
            'ticket': ticket,
        }
        self.send('acceptUser', self.cmd_id, callback=callback, data=data)

    def add_contact(self, stranger: str, ticket: str, type=3, content="",
                    callback='add_contact_callback'):
        '''
        主动添加好友
        :param stranger: 用户stranger数据
        :param ticket: 用户ticket数据
        :param type: int 添加好友途径
        :param content: 验证信息
        :param callback: 
        :return: 
        '''
        data = {
            'stranger': stranger,
            'ticket': ticket,
            'type': type,
            'content': content,
        }
        self.send('addContact', self.cmd_id, callback=callback, data=data)

    def say_hello(self, stranger: str, ticket: str, content: str,
                  callback='say_hello_callback'):
        '''
        打招呼
        :param stranger: 用户stranger数据
        :param ticket: 用户ticket数据
        :param content: 找招呼内容
        :param callback: 
        :return: 
        '''
        data = {
            'stranger': stranger,
            'ticket': ticket,
            'content': content,
        }
        self.send('sayHello', self.cmd_id, callback=callback, data=data)

    def delete_contact(self, username: str, callback='delete_contact_callback'):
        '''
        删除好友
        :param username: 用户wxid
        :param callback: 
        :return: 
        '''
        data = {
            'userId': username
        }
        self.send('deleteContact', self.cmd_id, callback=callback, data=data)

    def set_remark(self, username: str, remark: str,
                   callback='set_remark_callback'):
        '''
        设置好友备注
        :param username: 用户wxid
        :param remark: 备注内容
        :param callback: 
        :return: 
        '''
        data = {
            'userId': username,
            'remark': remark
        }
        self.send('setRemark', self.cmd_id, callback=callback, data=data)

    def set_head_img(self, file: Union[io.FileIO, str],
                     callback='set_head_img_callback'):
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
        self.send('setHeadImg', self.cmd_id, callback=callback, data=data)

    def sync_msg(self, callback='sync_msg_callback'):
        '''
        主动同步消息
        :param callback: 
        :return: 
        '''
        self.send('syncMsg', self.cmd_id, callback=callback)

    def sync_contact(self, reset=False, callback='sync_contact_callback'):
        '''
        同步通讯录
        :param reset: 若设置为true，会重置同步状态
        :param callback: 
        :return: 
        '''
        data = {
            'reset': bool(reset)
        }
        self.send('syncContact', self.cmd_id, callback=callback, data=data)

    def get_user_qrcode(self, username=None, style=0,
                           callback='get_user_qrcode_callback'):
        '''
        获取个人二维码(仅限自己)
        :param username: 用户wxid
        :param stype: int 二维码风格0-3
        :param callback: 
        :return: 
        '''
        data = {
            'userId': username or self.user.wx_id,
            'style': style,
        }
        self.send('getUserQrcode', self.cmd_id, callback=callback, data=data)

    def get_my_info(self, callback='get_my_info_callback'):
        '''
        获取个人资料
        :param callback: 
        :return: 
        '''
        self.send('getMyInfo', self.cmd_id, callback=callback)

    # 群管理 接口 ###############################################################
    def create_room(self, user_list: list, callback='create_room_callback'):
        '''
        创建群
        备注：必须多于2个人（含2个），才会建群成功
        :param user_list: 用户wxid列表
        :param callback: 
        :return: 
        '''
        data = {
            'userList': user_list
        }
        self.send('createRoom', self.cmd_id, callback=callback, data=data)

    def get_room_members(self, group_id: str, callback='get_room_members_callback'):
        '''
        获取群成员
        :param group_id: 群id
        :param callback: 
        :return: 
        '''
        data = {
            'groupId': group_id
        }
        self.send('getRoomMembers', self.cmd_id, callback=callback, data=data)

    def add_room_member(self, group_id: str, username: str,
                        callback='add_room_member_callback'):
        '''
        添加群成员
        :param group_id: 群id
        :param username: 用户wxid
        :param callback: 
        :return: 
        '''
        data = {
            'groupId': group_id,
            'userId': username,
        }
        self.send('addRoomMember', self.cmd_id, callback=callback, data=data)

    def invite_room_member(self, group_id: str, username: str,
                         callback='invite_room_member_callback'):
        '''
        邀请群成员
        :param group_id: 群id
        :param username: 用户wxid
        :param callback: 
        :return: 
        '''
        data = {
            'groupId': group_id,
            'userId': username,
        }
        self.send('inviteRoomMember', self.cmd_id, callback=callback, data=data)

    def delete_room_member(self, group_id: str, username: str,
                         callback='delete_room_member_callback'):
        '''
        删除群成员
        :param group_id: 群id
        :param username: 用户wxid
        :param callback: 
        :return: 
        '''
        data = {
            'groupId': group_id,
            'userId': username,
        }
        self.send('deleteRoomMember', self.cmd_id, callback=callback, data=data)

    def quit_room(self, group_id: str, callback='quit_room_callback'):
        '''
        退群
        :param group_id: 群id
        :param callback: 
        :return: 
        '''
        data = {
            'groupId': group_id
        }
        self.send('quitRoom', self.cmd_id, callback=callback, data=data)

    def set_room_announcement(self, group_id: str, content: str,
                            callback='set_room_announcement_callback'):
        '''
        设置群公告
        :param group_id: 群id
        :param content: 公告内容
        :param callback: 
        :return: 
        '''
        data = {
            'groupId': group_id,
            'content': content
        }
        self.send('setRoomAnnouncement', self.cmd_id, callback=callback,
                  data=data)

    def set_room_name(self, group_id: str, content: str,
                    callback='set_room_name_callback'):
        '''
        设置群名称
        :param groupd_id: 群id
        :param content: 群名称
        :param callback: 
        :return: 
        '''
        data = {
            'groupId': group_id,
            'content': content
        }
        self.send('setRoomName', self.cmd_id, callback=callback, data=data)

    def get_room_qrcode(self, group_id: str,
                        callback='get_room_qrcode_callback'):
        '''
        获取群二维码
        :param group_id: 群id
        :param callback: 
        :return: 
        '''
        data = {
            'groupId': group_id
        }
        self.send('getRoomQrcode', self.cmd_id, callback=callback, data=data)

    # 消息 接口 #################################################################
    def send_msg(self, to_user_name: str, content: str, at_list: list=None,
                 callback='send_msg_callback'):
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
        self.send('sendMsg', self.cmd_id, callback=callback, data=context)

    def send_app_msg(self, username: str, title: str, des: str, url: str,
                   thumburl: str, appid=None, sdkver=None,
                   callback='send_app_msg_callback'):
        '''
        发送App消息
        :param username: 接收者wxid
        :param title: 标题
        :param des: 描述
        :param url: 链接url
        :param thumburl: 缩略图url
        :param appid: appid，可忽略
        :param sdkver: sdk版本，可忽略
        :param callback: 
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
        self.send('sendAppMsg', self.cmd_id, callback=callback, data=data)

    def send_image(self, username: str, file: Union[io.FileIO, str],
                  callback='send_image_callback'):
        '''
        发送图片
        :param username: 接收者wxid
        :param file: 二进制文件或base64字符串
        :param callback: 
        :return: 
        '''
        if hasattr(file, 'read'):
            file = base64.encodebytes(file.read()).decode()
        data = {
            'toUserName': username,
            'file': file
        }
        self.send('sendImage', self.cmd_id, callback=callback, data=data)

    def send_voice(self, username: str, file: Union[io.FileIO, str], time: int,
                   callback='send_voice_callback'):
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
        self.send('sendVoice', self.cmd_id, callback=callback, data=data)

    def share_card(self, username: str, content: str, user_id: str,
                  callback='share_card_callback'):
        '''
        分享名片
        :param username: 接收者id
        :param content: 分享内容
        :param user_id: 被分享者id
        :param callback: 
        :return: 
        '''
        data = {
            'toUserName': username,
            'content': content,
            'userId': user_id
        }
        self.send('shareCard', self.cmd_id, callback=callback, data=data)


    # 转账 接口 #################################################################
    def query_transfer(self, raw_data, callback='query_transfer_callback'):
        '''
        查看转账消息
        :param raw_data: 拿到的push数据，就是raw_data，不用做任何处理
        :param callback: 
        :return: 
        '''
        if 'rawMsgData' not in raw_data:
            raw_data = {'rawMsgData': raw_data}
        self.send('queryTransfer', self.cmd_id, callback=callback,
                  data=raw_data)

    def accept_transfer(self, raw_data, callback='accept_transfer_callback'):
        '''
        接受转账
        :param raw_data: 拿到的push msg消息，就是raw_data，不用做任何处理
        :param callback: 
        :return: 
        '''
        if 'rawMsgData' not in raw_data:
            raw_data = {'rawMsgData': raw_data}
        self.send('acceptTransfer', self.cmd_id, callback=callback,
                  data=raw_data)

    # 红包 接口 #################################################################

    def receive_red_packet(self, raw_data, callback='receive_red_packet_callback'):
        '''
        接收红包
        该接口并未正式领取红包，但领取红包前必须调用该函数，然后在该指令的回调函数中，或稍后
        再发送领取红包指令。
        领取红包以及查看红包信息，都必须先调用该函数，否则会执行失败
        :param raw_data: 拿到的push数据，就是raw_data，不用做任何处理
        :param callback: 
        :return: 
        '''
        if 'rawMsgData' not in raw_data:
            raw_data = {'rawMsgData': raw_data}
        self.send('receiveRedPacket', self.cmd_id, callback=callback,
                  data=raw_data)

    def open_red_packet(self, raw_data, key, callback='open_red_packet_callback'):
        '''
        领取红包
        :param raw_data: 拿到的push数据，就是raw_data，不用做任何处理
        :param key: 从接收红包接口中获取
        :param callback: 
        :return: 
        '''
        if 'rawMsgData' not in raw_data:
            raw_data = {
                'rawMsgData': raw_data,
            }
        raw_data.update({'key': key})
        self.send('openRedPacket', self.cmd_id, callback=callback,
                  data=raw_data)

    def query_red_packet(self, raw_data, key, callback='query_red_packet_callback'):
        '''
        查看红包信息
        :param raw_data: 拿到的push数据，就是raw_data，不用做任何处理
        :param key: 从接收红包接口中获取
        :param callback: 
        :return: 
        '''
        if 'rawMsgData' not in raw_data:
            raw_data = {'rawMsgData': raw_data}
        self.send('queryRedPacket', self.cmd_id, callback=callback,
                  data=raw_data)

