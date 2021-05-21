from rest_framework.generics import ListCreateAPIView

from users.models import User
from ..serializers.users import UserSerializer
from ..utils import MyPagination


class UserView(ListCreateAPIView):
    """获取用户, 新增用户"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = MyPagination

    def get_queryset(self):
        """重写获取查询集方法"""
        username = self.request.query_params.get('keyword')
        if username:
            return User.objects.filter(username__contains=username)
        else:
            return User.objects.all()