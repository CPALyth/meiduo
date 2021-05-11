# -*- coding:utf-8 -*-

import ssl
ssl._create_default_https_context =ssl._create_stdlib_context # 解决Mac开发环境下，网络错误的问题

from celery_tasks.sms.yuntongxun.CCPRestSDK import REST

# 说明：主账号，登陆云通讯网站后，可在"控制台-应用"中看到开发者主账号ACCOUNT SID
_accountSid = '8a216da878d425020178ea9e6d1d082e'

# 说明：主账号Token，登陆云通讯网站后，可在控制台-应用中看到开发者主账号AUTH TOKEN
_accountToken = 'ca1592d37d1d49a888267efa3513e75c'

# 请使用管理控制台首页的APPID或自己创建应用的APPID
_appId = '8a216da878d425020178ea9e6e2c0835'

# 说明：请求地址，生产环境配置成app.cloopen.com
_serverIP = 'app.cloopen.com'

# 说明：请求端口 ，生产环境为8883
_serverPort = "8883"

# 说明：REST API版本号保持不变
_softVersion = '2013-12-26'

class CCP():
    """发送短信验证码的单例类"""
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            # 如果单例不存在, 初始化单例
            cls._instance = super().__new__(cls, *args, **kwargs)
            # 初始化REST SDK
            cls._instance.rest = REST(_serverIP, _serverPort, _softVersion)
            cls._instance.rest.setAccount(_accountSid, _accountToken)
            cls._instance.rest.setAppId(_appId)
        return cls._instance

    def send_template_sms(self, to, datas, tempId):
        """
        发送短信验证码单例方法
        :param to: 手机号
        :param datas: 内容数据
        :param tempId: 模板ID
        :return: 成功0, 失败-1
        """
        result = self.rest.sendTemplateSMS(to, datas, tempId)
        print(result)
        if result.get('statusCode') == '000000':
            return 0
        else:
            return -1


if __name__ == '__main__':
    # 注意： 测试的短信模板编号为1
    ret = CCP().send_template_sms('15622746858', ['123456', 5], 1)
    print(ret)
