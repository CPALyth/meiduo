from rest_framework import serializers
from goods.models import SPUSpecification, SPU

class SpecsSerializer(serializers.ModelSerializer):
    """商品规格序列化器"""
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = SPUSpecification
        fields = ['id', 'name', 'spu', 'spu_id']


class SPUSerializer(serializers.ModelSerializer):
    """SPU序列化器"""
    class Meta:
        model = SPU
        fields = ['id', 'name']