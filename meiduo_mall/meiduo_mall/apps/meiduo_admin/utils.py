from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'username': user.username,
        'id': user.id,
    }

class MyPagination(PageNumberPagination):
    """自定义分页器"""
    page_size = 3  # 每页数量
    max_page_size = 4  # 前端最多能设置的每页数量
    page_query_param = 'page'  # page_query_param 前端发送的页数关键字名，默认为"page"
    page_size_query_param = 'pagesize'  # 前端发送的每页数目关键字名，默认为None

    def get_paginated_response(self, data):
        """改写分页器返回结果"""
        return Response(OrderedDict([
            ('counts', self.page.paginator.count),
            ('lists', data),
            ('page', self.page.number),
            ('pages', self.page.paginator.num_pages),
            ('pagesize', len(data)),
        ]))