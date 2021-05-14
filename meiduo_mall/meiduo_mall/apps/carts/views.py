import base64
import json
import pickle

from django.shortcuts import render
from django.views import View
from django import http
from django_redis import get_redis_connection

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE
from .utils import get_cart_dict_from_cookie, cart_dict_to_str, cart_str_to_dict


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
            return http.JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必传参数'})

        try:
            SKU.objects.get(id=sku_id)
        except:
            return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg': '参数sku_id错误'})

        try:
            count = int(count)
        except:
            return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg': '参数count错误'})

        if not isinstance(selected, bool):
            return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg': '参数selected错误'})

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
            cart_str = cart_dict_to_str(cart_dict)
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

    def put(self, request):
        """修改购物车"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)

        # 判断参数是否齐全
        if not all([sku_id, count]):
            return http.JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少必传参数'})
        # 判断sku_id是否存在
        try:
            sku = SKU.objects.get(id=sku_id)
        except:
            return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg': '参数sku_id错误'})
        # 判断count是否为数字
        try:
            count = int(count)
        except Exception:
            return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg': '参数count有误'})
        # 判断selected是否为bool值
        if not isinstance(selected, bool):
            return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg': '参数selected有误'})

        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 用户已登录，修改redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 设置商品件数
            pl.hset('carts_{}'.format(user.id), sku_id, count)
            # 修改勾选状态
            if selected:
                pl.sadd('selected_{}'.format(user.id), sku_id)
            else:
                pl.srem('selected_{}'.format(user.id), sku_id)
            # 执行
            pl.execute()
            # 构造响应数据
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'price': sku.price,
                'amount': sku.price * count,
                'default_image_url': sku.default_image.url,
            }
            # 响应结果
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_sku': cart_sku})
        else:
            # 用户未登录，修改cookie购物车
            cart_dict = get_cart_dict_from_cookie(request)
            # 覆盖写入
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected,
            }
            # 构造响应数据
            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'price': sku.price,
                'amount': sku.price * count,
                'default_image_url': sku.default_image.url,
            }
            # 将购物车字典变为字符串
            cart_str = cart_dict_to_str(cart_dict)
            # 将新的购物车数据写到cookie
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_sku': cart_sku})
            response.set_cookie('carts', cart_str)
            return response

    def delete(self, request):
        """删除购物车"""
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        # 判断sku_id是否存在
        try:
            SKU.objects.get(id=sku_id)
        except:
            return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg': '参数sku_id错误'})
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 用户已登录, 删除redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            pl.hdel('carts_{}'.format(user.id), sku_id)
            pl.srem('selected_{}'.format(user.id), sku_id)
            pl.execute()
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
        else:
            # 用户未登录, 删除cookie购物车
            cart_dict = get_cart_dict_from_cookie(request)
            # 构造响应对象
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
            if sku_id in cart_dict:
                del cart_dict[sku_id]
                # 将购物车字典变为字符串
                cart_str = cart_dict_to_str(cart_dict)
                # 响应写入新cookie
                response.set_cookie('carts', cart_str)
            return response


class CartsSelectAllView(View):
    """全选购物车"""
    def put(self, request):
        # 接收参数
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected', True)
        # 校验参数
        if not isinstance(selected, bool):
            return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg': '参数selected有误'})
        # 判断用户是否登录
        user = request.user
        if user.is_authenticated:
            # 用户已登录, 操作redis购物车
            redis_conn = get_redis_connection('carts')
            redis_cart = redis_conn.hgetall('carts_{}'.format(user.id))
            redis_sku_ids = redis_cart.keys()
            # 用户是否全选
            if selected:
                # 全选
                redis_conn.sadd('selected_{}'.format(user.id), *redis_sku_ids)
            else:
                # 取消全选
                redis_conn.srem('selected_{}'.format(user.id), *redis_sku_ids)
            # 响应结果
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
        else:
            # 用户未登录, 操作cookie购物车
            cart_str = request.COOKIES.get('carts')
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

            if cart_str:
                cart_dict = cart_str_to_dict(cart_str)
                # 遍历所有的购物车记录
                for sku_id in cart_dict:
                    cart_dict[sku_id]['selected'] = selected
                # 将购物车字典变为字符串
                cart_str = cart_dict_to_str(cart_dict)
                # 将新的购物车数据写到cookie
                response.set_cookie('carts', cart_str)
            # 响应结果
            return response


class CartsSimpleView(View):
    """商品页面右上角购物车"""
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            # 查询redis购物车
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
            # 查询cookie购物车
            cart_dict = get_cart_dict_from_cookie(request)
        sku_ids = cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)
        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': cart_dict[sku.id].get('count'),
                'default_image_url': sku.default_image.url,
            })
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_skus': cart_skus})
