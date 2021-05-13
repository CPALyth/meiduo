from collections import OrderedDict

from django.shortcuts import render
from django.views import View

from .models import ContentCategory
from goods.models import GoodsChannel

class IndexView(View):
    """首页广告"""
    def get(self, request):
        """提供首页广告界面"""
        # --------------------- 准备商品分类对应的字典 ---------------------
        categories = OrderedDict()
        channels = GoodsChannel.objects.order_by('group_id', 'sequence')
        # 遍历所有频道
        for channel in channels:
            group_id = channel.group_id
            if group_id not in categories:
                categories[group_id] = {'channels': [], 'sub_cats': []}
            cat1 = channel.category
            categories[group_id]['channels'].append({
                'id': cat1.id,
                'name': cat1.name,
                'url': channel.url,
            })
            for cat2 in cat1.subs.all():
                cat2.sub_cats = []
                for cat3 in cat2.subs.all():
                    cat2.sub_cats.append({
                        'id': cat3.id,
                        'name': cat3.name,
                    })
                categories[group_id]['sub_cats'].append({
                    'id': cat2.id,
                    'name': cat2.name,
                    'sub_cats': cat2.sub_cats,
                })
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


