from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from goods.models import SKUImage, SKU
from ..serializers.images import ImagesSerializer, SKUSerializer
from ..utils import MyPagination

class ImagesView(ModelViewSet):
    """商品图片的增删改查"""
    queryset = SKUImage.objects.all()
    serializer_class = ImagesSerializer
    pagination_class = MyPagination
    permission_classes = [IsAdminUser]

    def simple(self, request):
        """获取商品SKU信息"""
        skus = SKU.objects.all()
        ser = SKUSerializer(skus, many=True)
        return Response(ser.data)

