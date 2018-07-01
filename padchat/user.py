import os
import pickle
from .logger import logger


class User:
    '''
        {
            "email":"",
            "external":"1",
            "long_link_server":"",
            "message":"Everything is ok",
            "nick_name":"测试",
            "phone_number":"",
            "qq":111111,
            "short_link_server":"",
            "status":0,
            "uin":111111,
            "user_name":"wxid_xxxxx"
        }
    '''
    email = None
    external = None # unknow
    long_link_server = None # unknow
    message = None # unknow
    nick_name = None
    phone_number = None
    qq = None
    short_link_server = None # unknow
    status = None
    uin = None # 微信唯一标示
    user_name = None # wxid
    device_type = None # 登录设备
    expired_time = None # 超时时间？
    head_url = None # 头像url
    sub_status = None # 登录状态
    password = None # 登录密码

    def __init__(self, user_name, alive=True, **kwargs):
        self.user_name = user_name
        for key, value in kwargs.items():
            if key not in dir(self):
                logger.warn('user info unknow key: "{key}" value: "{value}'.format(
                    key=key, value=value
                ))
            else:
                setattr(self, key, value)

        self.alive = alive

    def __bool__(self):
        return self.alive

    @property
    def wx_id(self):
        return self.user_name


class UserProfile:
    profile_file = os.path.join(os.getcwd(), 'profile')

    def __init__(self):
        if os.path.isfile(self.profile_file):
            self.profile_file_data = self.load()
        else:
            self.profile_file_data = []

    def __getitem__(self, key):
        return {i.get(key, getattr(i['user'], key, None)): i \
                for i in self.profile_file_data if i.get(
            key, hasattr(i['user'], key))}

    def save(self, user: User, wx_data, token):
        for i in self.profile_file_data:
            if i['user'].uin == user.uin:
                i['user'] = user
                i['wx_data'] = wx_data
                i['token'] = token
                break
        else:
            self.profile_file_data.append({'user': user, 'wx_data': wx_data,
                                           'token': token})
        self.dump()

    def dump(self):
        pickle.dump(self.profile_file_data, open(self.profile_file, 'wb'))

    def load(self):
        return pickle.load(open(self.profile_file, 'rb'))

