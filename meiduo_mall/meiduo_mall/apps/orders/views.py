from decimal import Decimal

from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django_redis import get_redis_connection

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
        # 查询redis购物车中的商品
        redis_conn = get_redis_connection('carts')
        redis_cart = redis_conn.hgetall('carts_{}'.format(user.id))
        # 被勾选的商品的sku_id
        redis_selected = redis_conn.smembers('selected_{}'.format(user.id))
        # 构造购物车中被勾选的商品字典 sku_id: count
        new_cart_dict = {
            int(key): int(val)
            for key, val in redis_cart.items()
            if key in redis_selected
        }
        # 获取skus
        sku_ids = new_cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        # 给sku添加数量和小计, 并计算总数量和总金额
        total_count = 0
        total_amount = 0
        for sku in skus:
            sku.count = new_cart_dict[sku.id]
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