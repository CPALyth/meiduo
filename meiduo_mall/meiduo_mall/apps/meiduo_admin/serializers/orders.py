from rest_framework import serializers

from orders.models import OrderInfo, OrderGoods, SKU


class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ('name', 'default_image')


class OrderGoodsSerializer(serializers.ModelSerializer):
    sku = SKUSerializer(read_only=True)

    class Meta:
        model = OrderGoods
        fields = ('count', 'price', 'sku')


class OrderInfoSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    skus = OrderGoodsSerializer(read_only=True, many=True)

    class Meta:
        model = OrderInfo
        fields = '__all__'  # ('order_id', 'create_time')
