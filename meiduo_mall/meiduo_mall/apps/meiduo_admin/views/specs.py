from rest_framework.viewsets import ModelViewSet

from goods.models import SPUSpecification
from ..serializer.specs import SpecsSerializer
from ..utils import MyPagination

class SpecsView(ModelViewSet):
    """商品规格的增删改查"""
    queryset = SPUSpecification.objects.all()
    serializer_class = SpecsSerializer
    pagination_class = MyPagination

