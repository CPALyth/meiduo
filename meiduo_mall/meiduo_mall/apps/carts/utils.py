import base64, pickle

from django_redis import get_redis_connection


def get_cart_dict_from_cookie(request):
    """从cookie中获取购物车字典"""
    cart_str = request.COOKIES.get('carts')
    if cart_str:
        cart_str_bytes = cart_str.encode()
        cart_dict_bytes = base64.b64decode(cart_str_bytes)
        cart_dict = pickle.loads(cart_dict_bytes)
    else:
        cart_dict = {}
    return cart_dict


def cart_dict_to_str(cart_dict):
    """购物车字典转字符串"""
    cart_dict_bytes = pickle.dumps(cart_dict)
    cart_str_bytes = base64.b64encode(cart_dict_bytes)
    cart_str = cart_str_bytes.decode()
    return cart_str


def cart_str_to_dict(cart_str):
    """购物车字符串转字典"""
    cart_str_bytes = cart_str.encode()
    cart_dict_bytes = base64.b64decode(cart_str_bytes)
    cart_dict = pickle.loads(cart_dict_bytes)
    return cart_dict


def merge_cart_cookie_redis(request, user, response):
    """合并购物车"""
    # 获取cookies中的购物车数据
    cookie_cart_dict = get_cart_dict_from_cookie(request)
    # 判断cookies中的购物车数据是否存在
    if not cookie_cart_dict:  # 如果不存在, 不需要合并
        return response
    # 准备容器, 保存新的sku_id:count,selected,unselected
    new_cart_dict = {}
    new_selected_add = []
    new_selected_rem = []
    # 遍历出cookie中的购物车数据
    for sku_id, cookie_dict in cookie_cart_dict.items():
        new_cart_dict[sku_id] = cookie_dict['count']
        if cookie_dict['selected']:
            new_selected_add.append(sku_id)
        else:
            new_selected_rem.append(sku_id)
    # 根据新的数据结构, 合并到redis
    redis_conn = get_redis_connection('carts')
    pl = redis_conn.pipeline()
    pl.hmset('carts_{}'.format(user.id), new_cart_dict)
    if new_selected_add:
        pl.sadd('selected_{}'.format(user.id), *new_selected_add)
    if new_selected_rem:
        pl.srem('selected_{}'.format(user.id), *new_selected_rem)
    pl.execute()
    # 删除cookie
    response.delete_cookie('carts')
    return response