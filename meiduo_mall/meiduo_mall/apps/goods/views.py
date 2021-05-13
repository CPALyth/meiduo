from django.shortcuts import render
from django.views import View
from django import http
from django.core.paginator import Paginator

from meiduo_mall.utils.response_code import RETCODE
from .models import GoodsCategory, SKU
from .utils import get_breadcrumb
from contents.utils import get_categories


class ListView(View):
    """商品列表页"""
    def get(self, request, category_id, page_num):
        """查询并渲染商品列表页"""
        # 接收参数
        sort = request.GET.get('sort', 'default')
        if sort == 'price':
            sort_field = 'price'
        elif sort == 'hot':
            sort_field = '-sales'
        else:
            sort = 'default'
            sort_field = 'create_time'
        # 校验参数
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except:
            return http.HttpResponseForbidden('参数category_id不存在')
        # 查询商品分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(category)

        # 排序
        skus = category.sku_set.filter(is_launched=True).order_by(sort_field)
        # 分页
        paginator = Paginator(skus, 5)  # 每页5条记录
        # 获取客户要看的那一页
        try:
            page_skus = paginator.page(page_num)
        except:
            return http.HttpResponseForbidden('页号不存在')
        # 获取总页数
        total_page = paginator.num_pages
        # 构造上下文
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'page_skus': page_skus,
            'total_page': total_page,
            'page_num': page_num,  # 此参数也可通过page_skus.number获取
            'sort': sort,
            'category_id': category_id,
        }
        return render(request, 'list.html', context)


class HotGoodsView(View):
    """热销排行"""
    def get(self, request, category_id):
        # 查询指定分类的SKU信息, 而且是上架, 按销量由高到低排序, 最后切片取出前两位
        skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:2]
        # 将模型列表转字典列表, 构造JSON数据
        hot_skus = []
        for sku in skus:
            hot_skus.append({
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price,
            })
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'hot_skus': hot_skus})