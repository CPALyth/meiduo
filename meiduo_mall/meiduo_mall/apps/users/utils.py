# 自定义用户认证的后端: 实现多账号登录
import re
from django.contrib.auth.backends import ModelBackend
from users.models import User


def get_user_by_acount(account):
    """
    通过账号获取用户
    :param account: 用户名或手机号
    :return: user
    """
    try:
        if re.match(r'^1[3-9]\d{9}$', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except:
        return None
    return user


class UsernameMobileBackend(ModelBackend):
    """自定义用户认证后端"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        重写用户认证的方法
        :param username: 用户名或手机号
        :param password: 密码明文
        :param kwargs: 额外参数
        :return: user
        """
        # 查询用户
        user = get_user_by_acount(username)
        # 使用账号查询用户
        if user and user.check_password(password):
            return user
        else:
            return None