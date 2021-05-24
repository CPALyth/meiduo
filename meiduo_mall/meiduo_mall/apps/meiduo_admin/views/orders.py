from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAdminUser

from orders.models import OrderInfo
from ..serializers.orders import OrderInfoSerializer, OrderSerializer
from ..utils import MyPagination


class OrderView(ReadOnlyModelViewSet):
    pagination_class = MyPagination
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderInfoSerializer
        return OrderSerializer

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword:
            return OrderInfo.objects.filter(order_id__contains=keyword)
        return OrderInfo.objects.all()
