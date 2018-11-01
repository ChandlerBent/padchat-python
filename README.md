Padchat-python-SDK
---

## 说明
该项目为[Padchat](https://github.com/binsee/padchat-sdk)的python SDK，具体接口用法
以 `Padchat` 接口文档为准。

Padchat SDK版本
* [padchat-sdk](https://github.com/binsee/padchat-sdk) - Padchat Node SDK，由
`Padchat` 服务开发者提供
* [padchat-php](https://github.com/fastgoo/padchat-php) - Padchat PHP SDK，由
[fastgoo] 开发者提供

## 更新历史

日期 | 内容
--- | ---
2018.10.16 | 添加图片、视频、语音下载接口。更改异步结构。
2018.8.9 | 修复未登陆情况触发ping事件
2018.8.8 | 支持sendMsg `atList` 参数。
2018.7.31 | 添加心跳事件，可在心跳事件中做其他操作。

### 运行环境
* python3.5 (测试环境为3.6)
* tornado


### 开发进度

功能 | 开发 | 测试
--- | --- | ---
登陆管理 | √ | √
用户管理 | √ | √
群管理 | √ | √
发送消息 | √ | √
获取图片、文件 | √ | √
朋友圈操作 | X | X
收藏操作 | X | X
标签管理 | X | X
接收转账及红包 | √ | √
公众号操作 | X | X

### 使用方法

#### 最基本使用，只需要5行

```python
import padchat

user = padchat.PadchatClient.select_user()

client = padchat.PadchatClient(**(user or {}))
client.connect('ws://52.80.34.207:7777')
client.run()
```

#### 文字消息异步推送

```python
import padchat
from tornado import gen

class CustomPadchatClient(padchat.PadchatClient):
    @gen.coroutine
    def person_text_msg(self, context):
        # 个人消息接口
        from_user = context.get('from_user')
        result = yield self.send_msg(from_user, '发送一条消息')
        if result.get('success') is True:
            print('发送成功')
        
    @gen.coroutine
    def group_text_msg(self, context):
        # 群组消息接口
        # dosomething
        pass
    
user = CustomPadchatClient.select_user()

client = CustomPadchatClient(**(user or {}))
client.connect('ws://52.80.34.207:7777')
client.run()
```

#### 领取红包
```python
import padchat
from tornado import gen

class CustomPadchatClient(padchat.PadchatClient):
    @gen.coroutine
    def red_packet_msg(self, context):
        result = yield self.receive_red_packet(context)
        key = result.get('data', {}).get('key')
        result = yield self.open_red_packet(context, key)
        if result.get('success') is True:
            print('领取红包成功')
```

#### 心跳事件

```python
import padchat

class CustomPadchatClient(padchat.PadchatClient):
    def ping(self):
        pass
        # 此处可以从redis或者消息组件中获取数据，主动推送消息。
    
user = CustomPadchatClient.select_user()

client = CustomPadchatClient(**(user or {}), ping_interval=30)
client.connect('ws://52.80.34.207:7777')
client.run()
```

接口调用请查看[Padchat](https://github.com/binsee/padchat-sdk)文档，或 `api.py`文件
中的方法，详细的使用方法也可查看test中的 `client.py`文件。


## 联系我
* wechat: BenT_Chen
* QQ: 289678097
* email: gulu.ben@gmail.com