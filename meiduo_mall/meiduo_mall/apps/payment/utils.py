import os

from alipay import AliPay
from django.conf import settings


def get_alipay_obj():
    alipay = AliPay(
        appid=settings.ALIPAY_APPID,
        app_notify_url=None,  # 默认回调url
        app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
        alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/alipay_public_key.pem"),
        sign_type="RSA2",
        debug=settings.ALIPAY_DEBUG
    )
    return alipay