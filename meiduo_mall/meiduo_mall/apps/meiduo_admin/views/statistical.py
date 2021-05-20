import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from users.models import User
from goods.models import GoodsVisitCount
from ..serializer.statistical import UserGoodsCountSerializer

class UserTotalCountView(APIView):
    """用户总数统计"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        now_date = datetime.date.today()
        # 获取用户总数
        count = User.objects.count()
        return Response({
            'count': count,
            'date': now_date,
        })

class UserDayIncrementView(APIView):
    """日增用户统计"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        now_date = datetime.date.today()
        # 获取当日注册用户数量 date_joined 记录创建账户时间
        count = User.objects.filter(date_joined__gte=now_date).count()
        return Response({
            'count': count,
            'date': now_date,
        })

class UserDayActiveView(APIView):
    """日活用户统计"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        now_date = datetime.date.today()
        # 获取日活用户个数
        count = User.objects.filter(last_login__gte=now_date).count()
        return Response({
            'count': count,
            'date': now_date,
        })


class UserDayOrderView(APIView):
    """今日下单用户数统计"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        now_date = datetime.date.today()
        # 获取今日下单用户数, 通过订单条件查询用户, 关联查询多查一
        count = User.objects.filter(orderinfo__create_time__gte=now_date).distinct().count()
        return Response({
            'count': count,
            'date': now_date,
        })

class UserMonthIncrementView(APIView):
    """月增用户数统计"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        now_date = datetime.date.today()
        # 获取29天前的日期
        start_date = now_date - datetime.timedelta(days=29)
        # 保存30天的用户数
        date_list = []
        for i in range(30):
            cur_date = start_date + datetime.timedelta(days=i)
            after_date = cur_date + datetime.timedelta(days=1)
            count = User.objects.filter(date_joined__gte=cur_date, date_joined__lte=after_date).count()
            date_list.append({
                'count': count,
                'date': cur_date,
            })
        return Response(date_list)


class UserGoodsCountView(APIView):
    """日分类商品访问量统计"""
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        now_date = datetime.date.today()
        # 获取今日分类商品访问量
        gvcs = GoodsVisitCount.objects.filter(date__gte=now_date)
        ser = UserGoodsCountSerializer(gvcs, many=True)
        return Response(ser.data)