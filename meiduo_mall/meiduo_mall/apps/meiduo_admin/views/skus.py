from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from goods.models import SKU, GoodsCategory
from ..utils import MyPagination
from ..serializers.skus import SKUSerializer, SKUCategorySerializer

class SKUView(ModelViewSet):
    """SKU表的增删改查"""
    serializer_class = SKUSerializer
    queryset = SKU.objects.all()
    pagination_class = MyPagination
    permission_classes = [IsAdminUser]

class SKUCategoryView(ListAPIView):
    """SKU三级分类-查询全部"""
    serializer_class = SKUCategorySerializer
    queryset = GoodsCategory.objects.filter(subs=None)  # 只查三级分类


