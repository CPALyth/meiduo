from rest_framework import serializers
from goods.models import GoodsVisitCount

class UserGoodsCountSerializer(serializers.ModelSerializer):
    # 指定返回字段
    category = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = GoodsVisitCount
        fields = ('category', 'count')
        