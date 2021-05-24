from rest_framework import serializers

from orders.models import OrderInfo, OrderGoods, SKU


class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ('name', 'default_image')


class OrderGoodsSerializer(serializers.ModelSerializer):
    """订单物品序列化器"""
    sku = SKUSerializer(read_only=True)

    class Meta:
        model = OrderGoods
        fields = ('count', 'price', 'sku')


class OrderInfoSerializer(serializers.ModelSerializer):
    """单个订单详细信息序列化器"""
    user = serializers.StringRelatedField()
    skus = OrderGoodsSerializer(read_only=True, many=True)

    class Meta:
        model = OrderInfo
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    """所有订单信息序列化器"""

    class Meta:
        model = OrderInfo
        fields = ('order_id', 'create_time')
