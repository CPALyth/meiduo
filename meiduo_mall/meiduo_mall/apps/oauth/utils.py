from itsdangerous import TimedJSONWebSignatureSerializer as Serialzer
from django.conf import settings
from itsdangerous import BadData

from . import constants

def generate_access_token(openid):
    """
    序列化openid
    :param openid: openid明文
    :return: token(openid密文)
    """
    # 创建序列化器对象
    s = Serialzer(settings.SECRET_KEY, constants.ACCESS_TOKEN_EXPIRES)
    # 准备待序列化的字典数据
    data = {'openid': openid}
    # 调用dumps方法进行序列化, 是bytes
    token = s.dumps(data)
    # 返回序列化后的数据, 是str
    return token.decode()


def check_access_token(access_token_openid):
    """
    反序列化openid
    :param access_token_openid: token(openid密文)
    :return: openid明文
    """
    # 创建序列化器对象, 和序列化时的对象参数保持相同
    s = Serialzer(settings.SECRET_KEY, constants.ACCESS_TOKEN_EXPIRES)
    # 反序列化openid密文
    try:
        data = s.loads(access_token_openid.encode())
    except BadData:  # openid密文过期
        return None
    # 返回openid明文
    return data.get('openid')