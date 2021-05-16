import os
from collections import OrderedDict

from django.template import loader
from django.conf import settings

from contents.models import ContentCategory
from contents.utils import get_categories


def gen_static_index_html():
    """静态化首页"""
    # ------------------- 查询并展示商品分类 -------------------
    categories = get_categories()
    # ------------------- 查询所有广告数据 -------------------
    contents = OrderedDict()
    # 先获取所有的广告类别
    content_categories = ContentCategory.objects.all()
    for content_category in content_categories:
        # 根据广告类别查询其对应的所有未下架的广告内容并排序
        contents[content_category.key] = content_category.content_set.filter(status=True).order_by('sequence')
    # 构造上下文
    context = {
        'categories': categories,
        'contents': contents
    }
    # ------------------- 渲染模板 -------------------
    # 获取模板文件
    template = loader.get_template('index.html')
    # 使用上下文渲染模板文件
    html_text = template.render(context)

    # ------------------- 将模板写入文件 -------------------
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)