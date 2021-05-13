from django.shortcuts import render
from django.views import View
from django import http

from .models import GoodsCategory
from .utils import get_breadcrumb
from contents.utils import get_categories


class ListView(View):
    """商品列表页"""
    def get(self, request, category_id, page_num):
        """查询并渲染商品列表页"""
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except:
            return http.HttpResponseForbidden('参数category_id不存在')
        # 查询商品分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(category)
        # 构造上下文
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
        }
        return render(request, 'list.html', context)