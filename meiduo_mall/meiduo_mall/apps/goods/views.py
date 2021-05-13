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


class DetailView(View):
    """商品详情页"""
    def get(self, request, sku_id):
        try:
            sku = SKU.objects.get(id=sku_id)
        except:
            return render(request, '404.html')
        # 查询商品分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)

        # 构建当前商品的规格键
        sku_specs = sku.specs.order_by('spec_id')
        sku_key = []  # [10, 12]
        for spec in sku_specs:
            sku_key.append(spec.option.id)
        # 获取当前商品的所有SKU
        skus = sku.spu.sku_set.all()
        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}  # {(8, 11): 3, (8, 12): 4, (9, 11): 5, (9, 12): 6, (10, 11): 7, (10, 12): 8}
        for s in skus:
            # 获取sku的规格参数, <QuerySet [<SKUSpecification: 颜色 - 金色>, <SKUSpecification: 内存 - 64GB>]>
            s_specs = s.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in s_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = s.id
        # 获取当前商品的规格信息 <QuerySet [<SPUSpecification: Apple iPhone 8 Plus: 颜色>, <SPUSpecification: Apple iPhone 8 Plus: 内存>]>
        goods_specs = sku.spu.specs.order_by('id')
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return http.HttpResponseForbidden('当前sku的规格信息不完整')

        for index, spec in enumerate(goods_specs):
            # 复制当前sku的规格键
            key = sku_key[:]
            # 该规格的选项<QuerySet [<SpecificationOption: Apple iPhone 8 Plus: 颜色 - 金色>, <SpecificationOption: Apple iPhone 8 Plus: 颜色 - 深空灰>, <SpecificationOption: Apple iPhone 8 Plus: 颜色 - 银色>]>
            spec_options = spec.options.all()
            for option in spec_options:
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                option.sku_id = spec_sku_map.get(tuple(key))
            spec.spec_options = spec_options

        # 构造上下文
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,
        }

        for spec in goods_specs:
            print(spec)

        return render(request, 'detail.html', context)
