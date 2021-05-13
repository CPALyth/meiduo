from collections import OrderedDict

from django.shortcuts import render
from django.views import View

from goods.models import GoodsChannel

class IndexView(View):
    """首页广告"""
    def get(self, request):
        """提供首页广告界面"""
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
        # 渲染模板的上下文
        context = {
            'categories': categories,
        }
        return render(request, 'index.html', context)


"""
{
    "1":{
        "channels":[
            {"id":1, "name":"手机", "url":"http://shouji.jd.com/"},
            {"id":2, "name":"相机", "url":"http://www.itcast.cn/"}
        ],
        "sub_cats":[
            {
                "id":38, 
                "name":"手机通讯", 
                "sub_cats":[
                    {"id":115, "name":"手机"},
                    {"id":116, "name":"游戏手机"}
                ]
            },
            {
                "id":39, 
                "name":"手机配件", 
                "sub_cats":[
                    {"id":119, "name":"手机壳"},
                    {"id":120, "name":"贴膜"}
                ]
            }
        ]
    },
    "2":{
        "channels":[],
        "sub_cats":[]
    }
}
"""