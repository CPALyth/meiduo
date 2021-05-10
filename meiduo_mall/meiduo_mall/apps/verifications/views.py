from django.shortcuts import render
from django.views import View
from django_redis import get_redis_connection
from django import http

from verifications.libs.captcha.captcha import captcha


class ImageCodeView(View):
    """图形验证码"""

    def get(self, request, uuid):
        """
        :param uuid: 通用唯一识别码, 用于唯一标识图形验证码属于哪个用户
        :return: image/jpg
        """
        # 生成图形验证码
        text, image = captcha.generate_captcha()

        # 保存图形验证码
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex("img_{}".format(uuid), 300, text)  # key, 过期时间秒, value

        # 响应图形验证码, MIME类型为'image/jpg'
        return http.HttpResponse(image, content_type='image/jpg')