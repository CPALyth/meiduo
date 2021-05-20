from rest_framework import serializers
from goods.models import SPUSpecification

class SpecsSerializer(serializers.ModelSerializer):
    """商品规格的增删改查"""
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = SPUSpecification
        fields = ['id', 'name', 'spu', 'spu_id']
