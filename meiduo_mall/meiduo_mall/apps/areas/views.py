import logging

from django.shortcuts import render
from django.views import View
from django import http

from .models import Area
from meiduo_mall.utils.response_code import RETCODE

logger = logging.getLogger('django')

class AreasView(View):
    """省市区三级联动"""
    def get(self, request):
        area_id = request.GET.get('area_id')
        if not area_id:  # 查询省级数据
            try:
                province_list = []
                province_model_list = Area.objects.filter(parent_id__isnull=True)
                for province in province_model_list:
                    province_list.append({
                        'id': province.id,
                        'name': province.name,
                    })
                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'province_list': province_list})
            except Exception as e:
                logger.error(e)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '查询省份数据错误'})
        else:  # 查询城市或区县数据
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
                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data': sub_data})
            except Exception as e:
                logger.error(e)
                return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '查询城市或区域数据错误'})
