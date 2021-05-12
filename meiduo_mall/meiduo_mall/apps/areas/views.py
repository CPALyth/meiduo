import logging

from django.shortcuts import render
from django.views import View
from django import http
from django.core.cache import cache

from .models import Area
from meiduo_mall.utils.response_code import RETCODE

logger = logging.getLogger('django')

class AreasView(View):
    """省市区三级联动"""
    def get(self, request):
        area_id = request.GET.get('area_id')
        if not area_id:  # 查询省级数据
            # 查询是否有缓存
            province_list = cache.get('province_list')
            if not province_list:
                try:
                    province_list = []
                    province_model_list = Area.objects.filter(parent_id__isnull=True)
                    for province in province_model_list:
                        province_list.append({
                            'id': province.id,
                            'name': province.name,
                        })
                    # 缓存省份列表, 默认存放到'default'CACHES中, 即0号redis数据库
                    cache.set('province_list', province_list, 3600)
                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '查询省份数据错误'})
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
        else:  # 查询城市或区县数据
            # 查询是否有缓存
            sub_data = cache.get('sub_area_' + area_id)
            if not sub_data:
                try:
                    parent_model = Area.objects.get(id=area_id)
                    sub_model_list = parent_model.subs.all()
                    subs = []
                    for sub_model in sub_model_list:
                        subs.append({
                            'id': sub_model.id,
                            'name': sub_model.name,
                        })
                    sub_data = {
                        'id': parent_model.id,
                        'name': parent_model.name,
                        'subs': subs,
                    }
                    # 缓存城市或区县
                    cache.set('sub_area_' + area_id, sub_data, 3600)
                except Exception as e:
                    logger.error(e)
                    return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '查询城市或区域数据错误'})
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})
