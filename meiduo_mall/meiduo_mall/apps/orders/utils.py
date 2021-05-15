from django_redis import get_redis_connection


def get_sel_cart_dict(user):
    # 查询redis购物车中的商品
    redis_conn = get_redis_connection('carts')
    redis_cart = redis_conn.hgetall('carts_{}'.format(user.id))
    # 被勾选的商品的sku_id
    redis_selected = redis_conn.smembers('selected_{}'.format(user.id))
    # 构造购物车中被勾选的商品字典 sku_id: count
    sel_cart_dict = {
        int(key): int(val)
        for key, val in redis_cart.items()
        if key in redis_selected
    }
    return sel_cart_dict