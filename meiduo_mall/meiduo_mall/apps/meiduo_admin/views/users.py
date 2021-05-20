from rest_framework.generics import ListAPIView

from users.models import User
from ..serializer.users import UserSerializer
from ..utils import MyPagination


class UserView(ListAPIView):
    """获取用户数据"""
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