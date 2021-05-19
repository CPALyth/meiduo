import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from users.models import User

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