import json
from decimal import Decimal
import datetime

from django import http
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredJsonMixin
from orders.models import OrderInfo, OrderGoods
from orders.utils import get_sel_cart_dict
from users.models import Address
from goods.models import SKU

class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""
    def get(self, request):
        """提供订单结算页面"""
        # 获取登录用户
        user = request.user
        # 查询地址信息
        try:
            addresses = Address.objects.filter(user=user, is_deleted=False)
        except:
            # 如果地址为空，渲染模板时会判断，并跳转到地址编辑页面
            addresses = None
        sel_cart_dict = get_sel_cart_dict(user)
        # 获取skus
        sku_ids = sel_cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        # 给sku添加数量和小计, 并计算总数量和总金额
        total_count = 0
        total_amount = 0
        for sku in skus:
            sku.count = sel_cart_dict[sku.id]
            sku.amount = sku.price * sku.count
            total_count += sku.count
            total_amount += sku.amount
        # 指定默认的邮费
        freight = Decimal(10.00)
        # 构造上下文
        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight,
        }
        return render(request, 'place_order.html', context)


class OrderCommitView(LoginRequiredJsonMixin, View):
    """提交订单"""
    def post(self, request):
        # 接收参数
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')

        # 校验参数
        if not all([address_id, pay_method]):
            return http.JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必传参数'})

        try:
            address = Address.objects.get(id=address_id)
        except:
            return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg': '参数address_id错误'})

        if pay_method not in OrderInfo.PAY_METHODS_ENUM.values():
            return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg': '参数pay_method错误'})

        # 获取订单编号
        user = request.user
        order_id = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '{:09d}'.format(user.id)
        # 保存订单基本信息
        order = OrderInfo.objects.create(
            order_id = order_id,
            user = user,
            address = address,
            total_count = 0,
            total_amount = Decimal(0.00),
            freight = Decimal(10.00),
            pay_method = pay_method,
            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        )
        # 保存订单商品信息
        sel_cart_dict = get_sel_cart_dict(user)
        sku_ids = sel_cart_dict.keys()
        for sku_id in sku_ids:
            # 读取最新的购物车商品信息
            sku = SKU.objects.get(id=sku_id)
            # 获取要提交订单的商品数量
            commit_count = sel_cart_dict[sku.id]
            # 若提交数量大于商品库存
            if commit_count > sku.stock:
                return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})
            # sku减库存 加销量
            sku.stock -= commit_count
            sku.sales += commit_count
            sku.save()
            # spu加销量
            spu = sku.spu
            spu.sales += commit_count
            spu.save()
            # 创建订单商品信息
            OrderGoods.objects.create(
                order = order,
                sku = sku,
                count = commit_count,
                price = sku.price,
            )
            # 累加订单商品的数量和总价到订单基本信息表
            order.total_count += commit_count
            order.total_amount += commit_count * sku.price
        # 最后再加运费
        order.total_amount += order.freight
        order.save()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'order_id': order_id})


class OrderSuccessView(LoginRequiredMixin, View):
    """提交订单成功页面"""
    def get(self, request):
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')

        context = {
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method,
        }
        return render(request, 'order_success.html', context)