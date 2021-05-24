from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAdminUser

from orders.models import OrderInfo
from ..serializers.orders import OrderInfoSerializer, OrderSerializer
from ..utils import MyPagination


class OrderView(ReadOnlyModelViewSet):
    queryset = OrderInfo.objects.all()
    serializer_class = OrderInfoSerializer
    pagination_class = MyPagination
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderInfoSerializer
        return OrderSerializer
