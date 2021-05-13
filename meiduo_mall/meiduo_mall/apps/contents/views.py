from collections import OrderedDict

from django.shortcuts import render
from django.views import View

from .models import ContentCategory
from .utils import get_categories
from goods.models import GoodsChannel

class IndexView(View):
    """首页广告"""
    def get(self, request):
        """提供首页广告界面"""
        # --------------------- 准备商品分类对应的字典 ---------------------
        categories = get_categories()
        # --------------------- 查询首页广告数据 ---------------------
        contents = OrderedDict()  # 用来装广告
        content_categories = ContentCategory.objects.all()
        for content_category in content_categories:
            key = content_category.key
            contents[key] = content_category.content_set.filter(status=True).order_by('sequence')
        # 渲染模板的上下文
        context = {
            'categories': categories,
            'contents': contents,
        }
        return render(request, 'index.html', context)


