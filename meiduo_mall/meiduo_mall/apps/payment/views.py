from alipay import AliPay
from django import http
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.conf import settings

from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredJsonMixin
from orders.models import OrderInfo
from .utils import get_alipay_obj


class PaymentView(LoginRequiredJsonMixin, View):
    """对接支付宝的支付接口"""
    def get(self, request, order_id):
        # 查询要支付的订单
        user = request.user
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '订单信息错误'})

        # 创建支付宝对象
        alipay = get_alipay_obj()

        # 生成登录支付宝连接
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject="美多商城%s" % order_id,
            return_url=settings.ALIPAY_RETURN_URL,
        )

        # 响应登录支付宝连接
        alipay_url = settings.ALIPAY_URL + "?" + order_string
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})

class PaymentStatusView(View):
    """保存订单支付结果"""
    def get(self, request):
        # QueryDict转为标准字典
        query_dict = request.GET.dict()
        # sign不能参与签名验证
        sign = query_dict.pop('sign')
        # 创建支付宝对象
        alipay = get_alipay_obj()
        # 检测链接是否是由支付宝重定向过来的
        success = alipay.verify(query_dict, sign)
        if not success:  # 订单支付失败，重定向到我的订单
            return redirect(reverse('orders:info'))
