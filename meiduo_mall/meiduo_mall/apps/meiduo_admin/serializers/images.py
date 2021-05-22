from django.conf import settings
from fdfs_client.client import Fdfs_client
from rest_framework import serializers

from goods.models import SKUImage, SKU


class ImagesSerializer(serializers.ModelSerializer):
    """商品图片序列化器"""
    class Meta:
        model = SKUImage
        fields = ['id', 'sku', 'image']

    def create(self, validated_data):
        # 创建FDFS客户端对象
        cli = Fdfs_client(settings.FDFS_CLIENT_PATH)
        # 读取文件
        request = self.context['request']
        file = request.FILES.get('image').read()
        # 上传文件
        ret = cli.upload_by_buffer(file)
        # 判断是否上传成功
        if ret['Status'] != 'Upload successed.':
            raise serializers.ValidationError({'error': '上传图片失败'})
        # 在数据库中新增图片
        sku_id = validated_data.get('sku').id
        image = ret['Remote file_id']
        sku_img = SKUImage.objects.create(sku_id=sku_id, image=image)
        return sku_img


class SKUSerializer(serializers.ModelSerializer):
    """SKU序列化器"""
    class Meta:
        model = SKU
        fields = ['id', 'name']