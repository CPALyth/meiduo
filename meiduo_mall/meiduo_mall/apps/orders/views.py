import json
from decimal import Decimal
import datetime

from django import http
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction

from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredJsonMixin
from orders.models import OrderInfo, OrderGoods
from orders.utils import get_sel_cart_dict
from users.models import Address
from goods.models import SKU
from . import constants

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

        with transaction.atomic():
            # 在数据库操作前创建保存点
            save_id = transaction.savepoint()
            try:
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
                    while True:  # 每个商品都有多次下单的机会, 直到库存不足
                        # 读取最新的购物车商品信息
                        sku = SKU.objects.get(id=sku_id)
                        # 获取原始的库存和销量
                        ori_stock = sku.stock
                        ori_sales = sku.sales
                        # 获取要提交订单的商品数量
                        commit_count = sel_cart_dict[sku.id]
                        # 若提交数量大于商品库存
                        if commit_count > sku.stock:
                            transaction.savepoint_rollback(save_id)  # 库存不足, 回滚
                            return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})
                        # 乐观锁实现并发下单, sku减库存 加销量
                        new_stock = ori_stock - commit_count
                        new_sales = ori_sales - commit_count
                        ret = SKU.objects.filter(stock=ori_stock, sales=ori_sales).update(stock=new_stock, sales=new_sales)
                        if ret == 0:  # 失败, 回去重新查看库存是否足够
                            continue
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
                        # 下单成功, 跳出循环
                        break
                # 最后再加运费
                order.total_amount += order.freight
                order.save()
            except:
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '下单失败'})
            # 提交事务
            transaction.savepoint_commit(save_id)
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


class UserOrderInfoView(LoginRequiredMixin, View):
    """我的订单"""
    def get(self, request, page_num):
        """提供我的订单页面"""
        user = request.user
        # 查询用户的所有订单
        orders = user.orderinfo_set.order_by('-create_time')
        # 遍历所有订单
        for order in orders:
            # 添加属性-订单状态
            order.status_name = OrderInfo.ORDER_STATUS_CHOICES[order.status - 1][1]
            # 添加属性-支付方式
            order.pay_method_name = OrderInfo.PAY_METHOD_CHOICES[order.pay_method - 1][1]
            order.sku_list = []
            # 查询订单商品
            order_goods = order.skus.all()
            # 遍历订单商品
            for order_good in order_goods:
                sku = order_good.sku
                sku.count = order_good.count
                sku.amount = sku.price * sku.count
                order.sku_list.append(sku)
        # 分页
        try:
            page_num = int(page_num)
            paginator = Paginator(orders, constants.ORDERS_LIST_LIMIT)
            page_orders = paginator.page(page_num)
            total_page = paginator.num_pages
        except:
            return http.HttpResponseNotFound('订单不存在')
        context = {
            'page_orders': page_orders,
            'total_page': total_page,
            'page_num': page_num,
        }
        return render(request, 'user_center_order.html', context)