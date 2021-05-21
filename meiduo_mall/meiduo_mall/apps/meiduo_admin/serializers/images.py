from rest_framework import serializers

from goods.models import SKUImage


class ImagesSerializer(serializers.ModelSerializer):
    """商品图片序列化器"""
    sku = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = SKUImage
        fields = ['id', 'sku', 'image']