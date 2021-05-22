from rest_framework import serializers

from goods.models import SKUImage, SKU


class ImagesSerializer(serializers.ModelSerializer):
    """商品图片序列化器"""
    class Meta:
        model = SKUImage
        fields = ['id', 'sku', 'image']


class SKUSerializer(serializers.ModelSerializer):
    """SKU序列化器"""
    class Meta:
        model = SKU
        fields = ['id', 'name']