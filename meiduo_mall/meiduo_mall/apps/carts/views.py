import base64
import json
import pickle

from django.shortcuts import render
from django.views import View
from django import http
from django_redis import get_redis_connection

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE
from .utils import get_cart_dict_from_cookie


class CartsView(View):
    """购物车管理"""
    def post(self, request):
        """添加购物车"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)
        # 校验参数
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')

        try:
            SKU.objects.get(id=sku_id)
        except:
            return http.HttpResponseForbidden('参数sku_id错误')

        try:
            count = int(count)
        except:
            return http.HttpResponseForbidden('参数count错误')

        if not isinstance(selected, bool):
            return http.HttpResponseForbidden('参数selected错误')

        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 如果用户已登录, 操作redis
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            pl.hincrby('carts_{}'.format(user.id), sku_id, count)
            # 保存商品勾选状态
            if selected:
                pl.sadd('selected_{}'.format(user.id), sku_id)
            # 执行
            pl.execute()
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
        else:
            # 如果用户未登录, 操作Cookie
            cart_dict = get_cart_dict_from_cookie(request)
            # 判断当前要添加的商品在cart_dict中是否存在
            if sku_id in cart_dict:
                # 此物品已加入购物车, 增量计算
                origin_count = cart_dict[sku_id]['count']
                count += origin_count
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected,
            }
            # 将购物车字典变为字符串
            cart_dict_bytes = pickle.dumps(cart_dict)
            cart_str_bytes = base64.b64encode(cart_dict_bytes)
            cart_str = cart_str_bytes.decode()
            # 将新的购物车数据写到cookie
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
            response.set_cookie('carts', cart_str)
            # 响应结果
            return response

    def get(self, request):
        """查询购物车"""
        user = request.user
        if user.is_authenticated:
            # 用户已登录, 查询redis购物车
            redis_conn = get_redis_connection('carts')
            redis_cart = redis_conn.hgetall('carts_{}'.format(user.id))
            redis_selected = redis_conn.smembers('selected_{}'.format(user.id))
            cart_dict = {}
            for key, val in redis_cart.items():
                sku_id = int(key)
                count = int(val)
                cart_dict[sku_id] = {
                    'count': count,
                    'selected': key in redis_selected,
                }
        else:
            # 用户未登录, 查询cookies购物车
            cart_dict = get_cart_dict_from_cookie(request)
        # 构造响应数据
        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'count': cart_dict.get(sku.id).get('count'),
                'selected': str(cart_dict.get(sku.id).get('selected')),  # Vue不能识别py的True
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),
                'amount': str(sku.price * cart_dict.get(sku.id).get('count')),
            })
        context = {
            'cart_skus': cart_skus
        }
        return render(request, 'cart.html', context)