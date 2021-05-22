from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.request import Request
from fdfs_client.client import Fdfs_client
from django.conf import settings

from goods.models import SKUImage, SKU
from ..serializers.images import ImagesSerializer, SKUSerializer
from ..utils import MyPagination

class ImagesView(ModelViewSet):
    """商品图片的增删改查"""
    queryset = SKUImage.objects.all()
    serializer_class = ImagesSerializer
    pagination_class = MyPagination
    permission_classes = [IsAdminUser]

    def simple(self, request: Request):
        """获取商品SKU信息"""
        # 获取所有SKU信息
        skus = SKU.objects.all()
        # 序列化
        ser = SKUSerializer(skus, many=True)
        return Response(ser.data)

    def create(self, request: Request, *args, **kwargs):
        # 获取前端数据
        data = request.data
        # 验证数据
        ser = self.get_serializer(data=data)
        ser.is_valid()
        # 创建FDFS客户端对象
        cli = Fdfs_client(settings.FDFS_CLIENT_PATH)
        # 读取文件
        file = request.FILES.get('image').read()
        # 上传文件
        ret = cli.upload_by_buffer(file)
        # 判断是否上传成功
        if ret['Status'] != 'Upload successed.':
            return Response({'error': '上传图片失败'})
        # 在数据库中新增图片
        sku_id = ser.validated_data.get('sku').id
        image = ret['Remote file_id']
        sku_img = SKUImage.objects.create(sku_id=sku_id, image=image)
        # 返回数据
        return Response({
            'id': sku_img.id,
            'sku': sku_img.sku_id,
            'image': sku_img.image.url,
        })
