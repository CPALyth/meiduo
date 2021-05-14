import base64, pickle

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