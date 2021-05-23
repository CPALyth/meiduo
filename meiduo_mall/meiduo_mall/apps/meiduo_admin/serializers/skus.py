from rest_framework import serializers
from goods.models import SKU, SKUSpecification, GoodsCategory, SPU


class SKUSpecSerializer(serializers.ModelSerializer):
    """SKU规格序列化器"""
    spec_id = serializers.PrimaryKeyRelatedField(read_only=True)
    option_id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = SKUSpecification
        fields = ('spec_id', 'option_id')


class SKUSerializer(serializers.ModelSerializer):
    """SKU表序列化器"""
    spu = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    specs = SKUSpecSerializer(read_only=True, many=True)

    class Meta:
        model = SKU
        fields = (
            'id', 'name', 'spu', 'spu_id', 'caption', 'category_id', 'category',
            'price', 'cost_price', 'market_price', 'stock', 'sales', 'is_launched',
            'specs'
        )


class SKUCategorySerializer(serializers.ModelSerializer):
    """SKU分类序列化器"""

    class Meta:
        model = GoodsCategory
        fields = ('id', 'name')
