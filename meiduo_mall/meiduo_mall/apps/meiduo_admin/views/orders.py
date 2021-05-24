from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

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

    @action(methods=['put'], detail=True)
    def status(self, request, pk):
        """
        pk: order_id
        """
        # 获取订单
        try:
            order = OrderInfo.objects.get(order_id=pk)
        except:
            return Response({'error': '订单编号错误'})
        # 修改状态
        status = request.data.get('status')
        if not status:
            return Response({'error': '缺少状态值'})
        order.status = status
        order.save()
        # 返回修改信息
        return Response({'order_id': pk, 'status': status})
