from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from goods.models import SKU
from ..utils import MyPagination
from ..serializers.skus import SKUSerializer

class SKUView(ModelViewSet):
    """SKU表的增删改查"""
    serializer_class = SKUSerializer
    queryset = SKU.objects.all()
    pagination_class = MyPagination
    permission_classes = [IsAdminUser]