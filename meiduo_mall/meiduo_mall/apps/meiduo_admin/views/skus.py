from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from goods.models import SKU, GoodsCategory, SPU
from ..utils import MyPagination
from ..serializers.skus import SKUSerializer, SKUCategorySerializer, SPUSpecSerializer

class SKUView(ModelViewSet):
    """SKU表的增删改查"""
    queryset = SKU.objects.all()
    serializer_class = SKUSerializer
    pagination_class = MyPagination
    permission_classes = [IsAdminUser]

    @action(methods=['get'], detail=False)
    def categories(self, request):
        """自定义方法, 获取所有商品三级分类数据"""
        categories = GoodsCategory.objects.filter(subs=None)
        ser = SKUCategorySerializer(categories, many=True)
        return Response(ser.data)

    def specs(self, request, pk):
        """获取SPU商品规格信息"""
        spu = SPU.objects.get(id=pk)
        spu_specs = spu.specs.all()
        ser = SPUSpecSerializer(spu_specs, many=True)
        return Response(ser.data)
