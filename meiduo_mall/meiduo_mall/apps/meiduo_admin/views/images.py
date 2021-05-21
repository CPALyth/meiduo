from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from goods.models import SKUImage
from ..serializers.images import ImagesSerializer
from ..utils import MyPagination

class ImagesView(ModelViewSet):
    """商品图片的增删改查"""
    queryset = SKUImage.objects.all()
    serializer_class = ImagesSerializer
    pagination_class = MyPagination
    permission_classes = [IsAdminUser]