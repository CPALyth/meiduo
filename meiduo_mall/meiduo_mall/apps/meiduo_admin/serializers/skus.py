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
    """SKU序列化器"""
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()
    category = serializers.StringRelatedField()
    category_id = serializers.IntegerField()
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


class SPUSpecOptionSerializer(serializers.ModelSerializer):
    """SPU规格选项序列化器"""

    class Meta:
        model = SpecificationOption
        fields = ('id', 'value')


class SPUSpecSerializer(serializers.ModelSerializer):
    """SPU规格序列化器"""
    spu = serializers.StringRelatedField()
    options = SPUSpecOptionSerializer(read_only=True, many=True)

    class Meta:
        model = SPUSpecification
        fields = ('id', 'name', 'spu', 'spu_id', 'options')
