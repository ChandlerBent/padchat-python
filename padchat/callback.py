#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author: Ben Chen
from .constant import LoginType
from .logger import logger


class PadChatCallbackMixin:
    '''
    回调Mixin
    '''
    def cmd_msg_callback_route(self, msg):
        '''
        请求回应回调路由
        '''
        type = msg.get('type')
        cmd_id = msg.get('cmdId')
        task_id = msg.get('taskId')
        data = msg.get('data')

        msg_task = self.pop_msg_queue(cmd_id)
        _callback = msg_task.get('callback')
        if _callback:
            callback = getattr(self, _callback, None)
            if callback:
                if hasattr(callback, '__call__'):
                    callback(data, msg_task.get('payload'))

    def init_callback(self, data, last_payload):
        if data.get('success') is True:
            self._init = True
            if self.user:
                self.login(type=LoginType.token, token=self._token)
            else:
                self.login(type=LoginType.qrcode)
            logger.info('初始化成功')
        else:
            logger.error('初始化失败')

    def get_wx_data_callback(self, data, last_payload):
        if not data.get('success'):
            logger.error('获取实例设备数据失败')
        else:
            wx_data = data['data'].get('wx_data')
            if wx_data:
                self._wx_data = wx_data
                logger.info('获取实例设备数据成功')
                if self.user:
                    # 如已登录，则把当前登录用户保存
                    self.save_user()

    def login_callback(self, data, last_payload):
        if data.get('success') is True:
            logger.debug(data.get('msg'))
        else:
            if data.get('data', {}).get('status') == -2023:
                logger.error('尝试断线重连失败，尝试其他登录方式')
                self.login(type=LoginType.request, token=self._token)
            elif data.get('data', {}).get('status') in (-2017, -100):
                logger.error('尝试toten登录失败，尝试其他登录方式')
                self.login(type=LoginType.qrcode)
            else:
                logger.error('登录请求失败')
                self.login(type=LoginType.qrcode)

    def get_login_token_callback(self, data, last_payload):
        logger.debug(data)
        token = data['data'].get('token')
        if token:
            self._token = token
            logger.info('获取登录Token成功')
            if self.user:
                # 如已登录，则把当前用户保存
                self.save_user()

    def logout_callback(self, data, last_payload):
        logger.info('微信账号已注销退出成功')

    def close_callback(self, data, last_payload):
        logger.info('退出机器人实例')

    def get_contact_callback(self, data, last_payload):
        # 获取用户资料回调
        pass

    def search_contact_callback(self, data, last_payload):
        # 搜索用户资料回调
        pass

    def accept_user_callback(self, data, last_payload):
        # 通过好友请求回调
        pass

    def add_contact_callback(self, data, last_payload):
        # 主动添加好友回调
        pass

    def say_hello_callback(self, data, last_payload):
        # 打招呼回调
        pass

    def delete_contact_callback(self, data, last_payload):
        # 删除好友回调
        pass

    def set_remark_callback(self, data, last_payload):
        # 设置好友备注回调
        pass

    def set_head_img_callback(self, data, last_payload):
        # 设置头像回调
        pass

    def sync_msg_callback(self, data, last_payload):
        # 主动同步消息回调
        pass

    def sync_contact_callback(self, data, last_payload):
        # 同步通讯录回调
        pass

    def get_user_qrcode_callback(self, data, last_payload):
        # 获取个人二维码回调
        pass

    def get_my_info_callback(self, data, last_payload):
        # 获取个人资料回调
        pass

    def create_room_callback(self, data, last_payload):
        # 创建群回调回调
        pass

    def get_room_members_callback(self, data, last_payload):
        # 获取群成员回调
        pass

    def add_room_member_callback(self, data, last_payload):
        # 添加群成员回调
        pass

    def invite_room_member_callback(self, data, last_payload):
        # 邀请群成员回调
        pass

    def delete_room_member_callback(self, data, last_payload):
        # 删除群成员回调
        pass

    def quit_room_callback(self, data, last_payload):
        # 退群回调
        pass

    def set_room_announcement_callback(self, data, last_payload):
        # 设置群公告回调
        pass

    def set_room_name_callback(self, data, last_paylaod):
        # 设置群名称
        pass

    def get_room_qrcode_callback(self, data, last_payload):
        # 获取群二维码
        pass

    def send_msg_callback(self, data, last_payload):
        # 发送文字消息回调
        pass

    def send_app_msg_callback(self, data, last_payload):
        # 发送App消息回调
        pass

    def send_image_callback(self, data, last_payload):
        # 发送图片消息回调
        pass

    def send_voice_callback(self, data, last_payload):
        # 发送语音消息回调
        pass

    def share_card_callback(self, data, last_payload):
        # 分享名片消息回调
        pass

    def query_transfer_callback(self, data, last_payload):
        # 查询转账信息回调
        pass

    def accept_transfer_callback(self, data, last_payload):
        # 接收转账回调
        pass

    def receive_red_packet_callback(self, data, last_payload):
        # 接收红包回调
        pass

    def open_red_packet_callback(self, data, last_payload):
        # 领取红包回调
        pass

    def query_red_packet_callback(self, data, last_payload):
        # 查看红包回调
        pass
