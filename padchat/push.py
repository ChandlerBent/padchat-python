#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author: Ben Chen


class PadchatPushMixin:
    def _is_group_msg(self, context):
        from_user = context.get('from_user')
        return from_user.endswith('@chatroom')

    def text_msg(self, context):
        '''
        文字信息
        :param context: 
        :return: 
        '''
        if self._is_group_msg(context):
            self.group_text_msg(context)
        else:
            self.person_text_msg(context)

    def person_text_msg(self, context):
        '''
        好友文字信息
        :param context: 
        :return: 
        '''
        pass

    def group_text_msg(self, context):
        '''
        群组文字信息
        :param context: 
        :return: 
        '''
        pass

    def self_text_msg(self, context):
        '''
        自己发送的文字信息
        :param context: 
        :return: 
        '''
        pass

    def app_msg(self, context):
        '''
        应用消息信息
        :param context: 
        :return: 
        '''
        pass

    def friend_invite_msg(self, context):
        '''
        朋友邀请好友信息
        example:
            content = context.get('content')
            stranger = re.search(r'encryptusername="(.+?)"', content)
            ticket = re.search(r' ticket="(.+?)"', content)
            if stranger and ticket:
                stranger = stranger.group(1)
                ticket = ticket.group(1)
                self.accept_user(stranger, ticket)
        :param context: 
        :return: 
        '''
        pass

    def add_friend_msg(self, context):
        '''
        添加好友成功消息
        :param context: 
        :return: 
        '''
        pass

    def transfer_msg(self, context):
        '''
        转账信息
        :param context: 
        :return: 
        '''
        pass

    def red_packet_msg(self, context):
        '''
        红包信息
        :param context: 
        :return: 
        '''
        pass

    def zhifu_msg(self, context):
        '''
        收款信息
        :param context: 
        :return: 
        '''
        pass