from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAdminUser

from orders.models import OrderInfo
from ..serializers.orders import OrderInfoSerializer
from ..utils import MyPagination


class OrderView(ReadOnlyModelViewSet):
    queryset = OrderInfo.objects.all()
    serializer_class = OrderInfoSerializer
    pagination_class = MyPagination
    permission_classes = [IsAdminUser]
