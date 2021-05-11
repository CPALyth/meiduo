import logging, random

from django.views import View
from django_redis import get_redis_connection
from django import http

from meiduo_mall.utils.response_code import RETCODE
from .libs.captcha.captcha import captcha
from .libs import constants

# 创建日志输出器
from .libs.yuntongxun.ccp_sms import CCP

logger = logging.getLogger('django')

class SMSCodeView(View):
    """短信验证码"""
    def get(self, request, mobile):
        """
        :param request: 请求对象
        :param mobile: 手机号
        :return: JSON
        """
        # 接收参数
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('uuid')
        # 校验参数
        if not all([mobile, image_code_client, uuid]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 提取图形验证码
        redis_conn = get_redis_connection('verify_code')
        redis_key = 'img_{}'.format(uuid)
        image_code_server = redis_conn.get(redis_key)
        if image_code_server is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码已失效'})
        # 删除图形验证码
        redis_conn.delete(redis_key)
        # 对比图形验证码
        image_code_server = image_code_server.decode()
        if image_code_client.lower() != image_code_server.lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入图形验证码有误'})
        # 生成短信验证码: 随机六位数字
        sms_code = '{:06d}'.format(random.randint(0, 999999))
        logger.info(sms_code)
        # 保存短信验证码
        redis_conn.setex(redis_key, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 发送短信验证码
        CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], constants.SEND_SMS_TEMPLATE_ID)
        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})




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
        redis_conn.setex("img_{}".format(uuid), constants.IMAGE_CODE_REDIS_EXPIRES, text)  # key, 过期时间秒, value

        # 响应图形验证码, MIME类型为'image/jpg'
        return http.HttpResponse(image, content_type='image/jpg')