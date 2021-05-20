from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from goods.models import SPUSpecification, SPU
from ..serializer.specs import SpecsSerializer, SPUSerializer
from ..utils import MyPagination

class SpecsView(ModelViewSet):
    """商品规格的增删改查"""
    queryset = SPUSpecification.objects.all()
    serializer_class = SpecsSerializer
    pagination_class = MyPagination

    def simple(self, request):
        """获取SPU商品信息"""
        spus = SPU.objects.all()
        ser = SPUSerializer(spus, many=True)
        return Response(ser.data)