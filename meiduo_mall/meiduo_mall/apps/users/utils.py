from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from .models import User
from . import constants


def generate_verify_email_url(user):
    """
    生成邮箱激活链接
    :param user: 当前登录用户
    :return: 邮箱激活链接
    """
    s = Serializer(settings.SECRET_KEY, constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    data = {'user_id': user.id, 'email': user.email}
    token = s.dumps(data)
    return settings.EMAIL_VERIFY_URL + '?token=' + token.decode()


def check_verify_email_token(token):
    """
    反序列化token, 获取user
    :param token: 序列化后的用户信息
    :return: user
    """
    s = Serializer(settings.SECRET_KEY, constants.VERIFY_EMAIL_TOKEN_EXPIRES)
    try:
        data = s.loads(token)
    except:
        return None
    user_id = data.get('user_id')
    email = data.get('email')
    try:
        user = User.objects.get(id=user_id, email=email)
    except:
        return None
    return user


class UsernameMobileBackend(ModelBackend):
    """自定义用户认证后端, 实现多账号登录"""
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        重写用户认证的方法
        :param username: 用户名或手机号
        :param password: 密码明文
        :param kwargs: 额外参数
        :return: user
        """
        # 判断账号
        front = kwargs.get('front', False)
        if front:  # 前台登录
            try:
                user = User.objects.get(username=username)
            except:
                try:
                    user = User.objects.get(mobile=username)
                except:
                    return None
        else:  # 后台登录
            try:
                user = User.objects.get(username=username, is_staff=True)
            except:
                return None
        # 判断密码
        if user and user.check_password(password):
            return user
        return None